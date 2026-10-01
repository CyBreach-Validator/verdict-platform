from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.kafka.producer import publish_verdict
from app.models.rule import Rule
from app.schemas.validator import ValidationRequest
from app.security.security import get_current_user
from app.services.validator_service import MalformedRuleQuery, validate_rule
from app.services.verdict_service import save_verdict
from app.utils.rule_hash_utils import compute_rule_id
from app.websocket.connection_manager import manager

# B11: this endpoint runs a rule, writes a verdict and broadcasts it, and it
# was reachable anonymously -- anyone could drive Delta's detection engine and
# inject arbitrary rows.
#
# B13: the router used to set `prefix="/validator"`, so the mounted route was
# POST /api/v2/validator/validate. The plan's endpoint list names
# POST /api/v2/validate, and no /api/v2/validate string existed anywhere in the
# repository. The prefix is removed so `include_router(..., prefix="/api/v2")`
# in main.py yields the documented path.
router = APIRouter(
    tags=["Validator"],
    dependencies=[Depends(get_current_user)],
)


def derive_rule_id(request: ValidationRequest) -> str:
    """The canonical content hash this validation attributes its verdict to.

    `compute_rule_id` hashes rule_name + query + rule_type + mitre_technique,
    which is exactly what `create_rule` passes when it stores a rule. This used
    to be inlined as
    `compute_rule_id(rule_name=request.action_id, query=request.rule_query)`,
    which hashed the *action id* as the rule name and omitted two components, so
    the digest could never equal any stored `rules.rule_id`.

    Extracted so the four-field contract is testable directly rather than being
    reimplemented in a test (a reimplementation keeps passing after a
    regression).
    """
    return compute_rule_id(
        rule_name=request.rule_name or request.action_id,
        query=request.rule_query,
        rule_type=request.rule_type,
        mitre_technique=request.mitre_technique,
    )


def resolve_rule(db: Session, rule_id: str):
    """Return the stored `rules` row for a canonical id, or None."""
    return db.query(Rule).filter(Rule.rule_id == rule_id).first()


@router.post("/validate")
async def validate(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    # m8: `validate_rule` raises `MalformedRuleQuery` for a rule query that
    # cannot be evaluated at all (unparseable JSON, or JSON that is not an
    # object). It was previously called bare, so a malformed `rule_query`
    # escaped as an unhandled `ValueError` and the client received a 500 for
    # what is a client-side input error. `MalformedRuleQuery` subclasses
    # `ValueError`, and a 422 is what the service docstring already claimed
    # this layer did.
    try:
        result = validate_rule(
            request.rule_query,
            request.event
        )
    except MalformedRuleQuery as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # B4: this used to hardcode `rule_id=1` and `rule_name="Suspicious
    # PowerShell"`, so every ad-hoc validation in the platform was attributed
    # to rule 1 and could not be joined to a rule at all. Derive the canonical
    # content hash instead: the same rule body then resolves to the same
    # `rule_id` on every pod, and to the stored row if Delta already has it.
    # See `derive_rule_id` for the four fields it hashes over.
    rule_id = derive_rule_id(request)

    rule = resolve_rule(db, rule_id)

    # A missing rule row used to fall through to `save_verdict`, which then
    # raised IntegrityError and surfaced as an opaque HTTP 500. Say what is
    # actually wrong instead: `verdict_events.rule_id` is a foreign key, so a
    # verdict cannot exist without the rule it came from.
    if rule is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No stored rule matches this validation "
                f"(rule_id={rule_id}). Create the rule first via "
                f"POST /api/v2/rules, or pass the same rule_name, rule_type "
                f"and mitre_technique that were used to create it -- the rule_id "
                f"is a content hash over exactly those fields."
            ),
        )

    regulatory_control_refs = rule.regulatory_control_refs

    # N-D11: `save_verdict` returns the one canonical v2.0 payload it persisted
    # from. The old code hand-built a *fourth* shape here -- it divided
    # `result["confidence"]` (already a 0..1 fraction) by 100 again, put Sigma
    # field names in `causal_chain`, hardcoded `mttd_seconds` to None, used the
    # action id as its own `matched_evidence_ref`, and sent
    # `saved_verdict.verdict_hash`, a digest computed over a tuple that is not
    # even part of the published contract. So the hash a consumer received never
    # matched the event it came in. All four transports now use `payload`.
    saved_verdict, payload = save_verdict(
        db=db,
        action_id=request.action_id,
        rule_id=rule_id,
        rule_name=rule.rule_name,
        verdict=result["status"],
        confidence=result["confidence"],
        event=request.event,
        causal_chain=result["causal_chain"],
        mttd_seconds=result["mttd_seconds"],
        matched_evidence_ref=result["matched_evidence_ref"],
        regulatory_control_refs=regulatory_control_refs,
    )

    # The WebSocket broadcast used to carry a raw DB-column dump
    # (`id`, `event_data`, `created_at`) that shared no field names with the
    # contract, so a dashboard could not line the two up.
    await manager.broadcast(
        {
            **payload,
            "verdict_id": saved_verdict.id,
            "rule_id": saved_verdict.rule_id,
            "rule_name": saved_verdict.rule_name,
        }
    )

    publish_verdict(payload)

    return {
        **payload,
        "verdict_id": saved_verdict.id,
        "rule_id": saved_verdict.rule_id,
        "rule_name": saved_verdict.rule_name,
        # Retained for callers that still read the raw rule-evaluation detail
        # (matched fields, not the causal chain).
        "matched_fields": result.get("matched_fields", []),
    }
