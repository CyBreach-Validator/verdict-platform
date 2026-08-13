import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.verdict import Verdict
from app.utils.hash_utils import generate_verdict_hash


def create_audit_log(
    db: Session,
    action: str,
    verdict_id: int,
    rule_id: int,
    rule_name: str,
    old_verdict: str = None,
    new_verdict: str = None,
    related_verdict_id: int = None,
    verdict_hash: str = None,
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
        verdict_hash=verdict_hash,
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
    verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not verdict:
        return None

    try:
        event_data = json.loads(verdict.event_data)
    except (TypeError, json.JSONDecodeError):
        return {
            "verdict_id": verdict.id,
            "immutable": False,
            "stored_hash": verdict.verdict_hash,
            "calculated_hash": None,
            "reason": "Invalid event data stored for verdict.",
        }

    calculated_hash = generate_verdict_hash(
        rule_id=verdict.rule_id,
        rule_name=verdict.rule_name,
        verdict=verdict.verdict,
        event_data=event_data,
    )

    immutable = calculated_hash == verdict.verdict_hash

    return {
        "verdict_id": verdict.id,
        "immutable": immutable,
        "stored_hash": verdict.verdict_hash,
        "calculated_hash": calculated_hash,
        "reason": (
            "Hash verification successful."
            if immutable
            else "Hash mismatch detected. Verdict data may have been modified."
        ),
    }