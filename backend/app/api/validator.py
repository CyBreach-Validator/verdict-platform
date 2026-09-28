from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.kafka.producer import publish_verdict
from app.models.rule import Rule
from app.schemas.validator import ValidationRequest
from app.security.security import get_current_user
from app.services.validator_service import validate_rule
from app.services.verdict_service import save_verdict
from app.utils.rule_hash_utils import compute_rule_id
from app.websocket.connection_manager import manager

# B11: this endpoint runs a rule, writes a verdict and broadcasts it, and it
# was reachable anonymously -- anyone could drive Delta's detection engine and
# inject arbitrary rows.
router = APIRouter(
    prefix="/validator",
    tags=["Validator"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/validate")
async def validate(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    result = validate_rule(
        request.rule_query,
        request.event
    )

    # B4: this used to hardcode `rule_id=1` and `rule_name="Suspicious
    # PowerShell"`, so every ad-hoc validation in the platform was attributed
    # to rule 1 and could not be joined to a rule at all. Derive the canonical
    # content hash instead: the same rule body then resolves to the same
    # `rule_id` on every pod, and to the stored row if Delta already has it.
    rule_id = compute_rule_id(
        rule_name=request.action_id,
        query=request.rule_query,
    )

    rule = (
        db.query(Rule)
        .filter(Rule.rule_id == rule_id)
        .first()
    )

    regulatory_control_refs = rule.regulatory_control_refs if rule else []

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
        rule_name=rule.rule_name if rule else request.action_id,
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
