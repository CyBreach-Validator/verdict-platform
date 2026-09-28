import json

from sqlalchemy.orm import Session

from app.contracts.verdict_event import normalize_verdict
from app.kafka.producer import (
    publish_corrected_verdict,
    publish_gap_closed_event,
)
from app.models.rule import Rule
from app.models.verdict import Verdict
from app.services.audit_log_service import create_audit_log
from app.services.validator_service import validate_rule
from app.services.verdict_service import build_verdict_payload


def revalidate_verdict(db: Session, verdict_id: int):
    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None

    # B6: `rule_id` is the canonical string key, not Delta's integer surrogate.
    rule = (
        db.query(Rule)
        .filter(Rule.rule_id == old_verdict.rule_id)
        .first()
    )

    if not rule:
        return None

    event = json.loads(old_verdict.event_data)

    validation_result = validate_rule(
        rule.query,
        event
    )

    new_verdict_status = normalize_verdict(validation_result["status"])

    # N-D10/N-D11: the corrected event and the gap-closed event are built by
    # the same serializer as a primary verdict, from the same real values --
    # no more three hand-rolled payloads that disagree with each other. The old
    # code put `matched_fields` (Sigma field *names*) in `causal_chain`, sent
    # `mttd_seconds: None`, and used the action id as its own evidence ref.
    payload = build_verdict_payload(
        action_id=old_verdict.action_id,
        verdict=new_verdict_status,
        confidence=validation_result["confidence"],
        causal_chain=validation_result["causal_chain"],
        mttd_seconds=validation_result["mttd_seconds"],
        matched_evidence_ref=validation_result["matched_evidence_ref"],
        regulatory_control_refs=rule.regulatory_control_refs or [],
    )

    # N-D13: the partial unique index on `content_hash` only covers *current*
    # (non-superseded) rows, so the old verdict has to be retired before the
    # replacement is inserted. This cannot be a single transaction: SQLAlchemy's
    # unit of work emits INSERTs before UPDATEs for the same mapper, so a
    # one-transaction flip would still order these the wrong way round and trip
    # the constraint. Hence an explicit commit between the two.
    old_verdict.is_superseded = True
    db.commit()

    new_verdict = Verdict(
        action_id=payload["action_id"],
        rule_id=rule.rule_id,
        rule_name=rule.rule_name,
        verdict=payload["verdict"],
        confidence=payload["confidence"],
        causal_chain=payload["causal_chain"],
        mttd_seconds=payload["mttd_seconds"],
        matched_evidence_ref=payload["matched_evidence_ref"],
        regulatory_control_refs=payload["regulatory_control_refs"],
        event_data=old_verdict.event_data,
        content_hash=payload["content_hash"],
        is_superseded=False,
        superseded_by=None
    )

    try:
        db.add(new_verdict)
        db.commit()
    except Exception:
        db.rollback()
        # The old verdict is the only current record for this action_id, so
        # leaving it superseded with no replacement would silently drop the
        # verdict out of every feed. Put it back before propagating.
        old_verdict.is_superseded = False
        db.commit()
        raise

    db.refresh(new_verdict)

    old_verdict.superseded_by = new_verdict.id

    db.commit()
    db.refresh(old_verdict)

    publish_corrected_verdict(payload)

    gap_closed = (
        normalize_verdict(old_verdict.verdict) == "Missed"
        and new_verdict.verdict == "Detected"
    )

    if gap_closed:
        # Identical payload: a gap-closed event is the same v2.0 verdict seen
        # on `cybreach.gap_closed.v2`, so consumers on either topic can
        # compare them directly.
        publish_gap_closed_event(payload)

    # NB: the dashboard's revalidation view filters on this exact action
    # string (`dashboard_service.get_revalidation_dashboard`); the previous
    # "REVALIDATION" spelling meant the dashboard was always empty.
    create_audit_log(
        db=db,
        action="REVALIDATED",
        verdict_id=new_verdict.id,
        rule_id=new_verdict.rule_id,
        rule_name=new_verdict.rule_name,
        old_verdict=old_verdict.verdict,
        new_verdict=new_verdict.verdict,
        related_verdict_id=old_verdict.id,
        content_hash=new_verdict.content_hash,
        details={
            "gap_closed": gap_closed
        }
    )

    # The dashboard's before/after panel renders ids, verdicts, hashes and a
    # numeric comparison for this response, and it was typed against a
    # `comparison`/`validation` structure the endpoint has never returned --
    # `revalidationResult.old_verdict.verdict` was `undefined` on a string, so
    # the panel rendered blank. Everything below is derived from the two real
    # rows; nothing is invented.
    return {
        "verdict_id": new_verdict.id,
        "previous_verdict_id": old_verdict.id,
        "old_verdict": {
            "id": old_verdict.id,
            "verdict": old_verdict.verdict,
            "confidence": old_verdict.confidence,
            "content_hash": old_verdict.content_hash,
            "created_at": old_verdict.created_at,
        },
        "new_verdict": {
            "id": new_verdict.id,
            "verdict": new_verdict.verdict,
            "confidence": new_verdict.confidence,
            "content_hash": new_verdict.content_hash,
            "created_at": new_verdict.created_at,
        },
        "gap_closed": gap_closed,
        "content_hash": new_verdict.content_hash,
        "comparison": {
            # Confidence, not a "score": there is no scoring model anywhere in
            # the platform, and 0.0-1.0 confidence is a real measured value.
            "old_confidence": old_verdict.confidence,
            "new_confidence": new_verdict.confidence,
            "delta": new_verdict.confidence - old_verdict.confidence,
            "improved": _severity(new_verdict.verdict) > _severity(
                old_verdict.verdict
            ),
            "gap_closed": gap_closed,
        },
        "validation": {
            "status": "Matched" if new_verdict.verdict == "Detected" else "Not Matched",
            "matched_fields": validation_result.get("matched_fields", []),
        },
    }


# Detection severity ordering, used only to answer "did re-validation make this
# verdict more serious". Higher is worse.
_SEVERITY_ORDER = {
    "NoData": 0,
    "Missed": 1,
    "Detected": 2,
}


def _severity(verdict: str) -> int:
    return _SEVERITY_ORDER.get(normalize_verdict(verdict), 0)
