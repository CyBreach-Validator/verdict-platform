import json

from sqlalchemy.orm import Session

from app.contracts.verdict_event import compute_content_hash
from app.models.audit_log import AuditLog
from app.models.verdict import Verdict


def create_audit_log(
    db: Session,
    action: str,
    verdict_id: int,
    rule_id: str,
    rule_name: str,
    old_verdict: str = None,
    new_verdict: str = None,
    related_verdict_id: int = None,
    content_hash: str = None,
    details: dict = None,
):
    audit_log = AuditLog(
        action=action,
        verdict_id=verdict_id,
        related_verdict_id=related_verdict_id,
        rule_id=rule_id,
        rule_name=rule_name,
        old_verdict=old_verdict,
        new_verdict=new_verdict,
        content_hash=content_hash,
        details=json.dumps(details) if details else None,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_all_audit_logs(db: Session):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


def get_audit_log_by_id(
    db: Session,
    audit_log_id: int
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.id == audit_log_id)
        .first()
    )


def verify_verdict_immutability(
    db: Session,
    verdict_id: int
):
    """Recompute the stored verdict's `content_hash` from its own fields.

    N-D13: the old implementation hashed `{rule_id, rule_name, verdict,
    event_data}` -- a tuple that does not even appear in the published v2.0
    event, so it verified a digest no consumer could reproduce. The digest now
    covers the seven contract fields, which is exactly what a consumer holding
    the event re-derives.
    """

    verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not verdict:
        return None

    recalculated = {
        "action_id": verdict.action_id,
        "verdict": verdict.verdict,
        "confidence": verdict.confidence,
        "causal_chain": verdict.causal_chain or [],
        "mttd_seconds": verdict.mttd_seconds,
        "matched_evidence_ref": verdict.matched_evidence_ref,
        "regulatory_control_refs": verdict.regulatory_control_refs or [],
    }

    calculated_hash = compute_content_hash(recalculated)

    immutable = calculated_hash == verdict.content_hash

    return {
        "verdict_id": verdict.id,
        "immutable": immutable,
        "stored_hash": verdict.content_hash,
        "calculated_hash": calculated_hash,
        "reason": (
            "Hash verification successful."
            if immutable
            else "Hash mismatch detected. Verdict data may have been modified."
        ),
    }
