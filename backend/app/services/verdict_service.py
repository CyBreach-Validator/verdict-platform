import json

from sqlalchemy.orm import Session

from app.models.verdict import Verdict
from app.utils.hash_utils import generate_verdict_hash
from app.kafka.producer import publish_corrected_verdict
from app.websocket.connection_manager import manager


def save_verdict(
    db: Session,
    rule_id: int,
    rule_name: str,
    verdict: str,
    event: dict
):
    verdict_hash = generate_verdict_hash(
        rule_id=rule_id,
        rule_name=rule_name,
        verdict=verdict,
        event_data=event
    )

    db_verdict = Verdict(
        rule_id=rule_id,
        rule_name=rule_name,
        verdict=verdict,
        event_data=json.dumps(event),
        verdict_hash=verdict_hash,
        is_superseded=False,
        superseded_by=None
    )

    db.add(db_verdict)
    db.commit()
    db.refresh(db_verdict)

    return db_verdict


def get_all_verdicts(db: Session):
    return db.query(Verdict).all()


def get_verdict_by_id(db: Session, verdict_id: int):
    return db.query(Verdict).filter(Verdict.id == verdict_id).first()


def get_verdicts_by_rule(db: Session, rule_id: int):
    return db.query(Verdict).filter(Verdict.rule_id == rule_id).all()


def correct_verdict(db: Session, verdict_id: int, new_verdict: str):
    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None

    event = json.loads(old_verdict.event_data)

    new_hash = generate_verdict_hash(
        rule_id=old_verdict.rule_id,
        rule_name=old_verdict.rule_name,
        verdict=new_verdict,
        event_data=event
    )

    corrected_verdict = Verdict(
        rule_id=old_verdict.rule_id,
        rule_name=old_verdict.rule_name,
        verdict=new_verdict,
        event_data=old_verdict.event_data,
        verdict_hash=new_hash,
        is_superseded=False,
        superseded_by=None
    )

    db.add(corrected_verdict)
    db.commit()
    db.refresh(corrected_verdict)

    old_verdict.is_superseded = True
    old_verdict.superseded_by = corrected_verdict.id

    db.commit()
    db.refresh(old_verdict)

    print("Publishing corrected verdict to Kafka...")

    corrected_event = {
        "action_id": str(
            event.get("action_id", corrected_verdict.id)
        ),
        "verdict": corrected_verdict.verdict,
        "confidence": 1.0 if corrected_verdict.verdict == "Detected" else 0.0,
        "causal_chain": [],
        "mttd_seconds": None,
        "matched_evidence_ref": str(
            event.get("action_id", corrected_verdict.id)
        ),
        "regulatory_control_refs": [],
        "content_hash": corrected_verdict.verdict_hash
    }

    publish_corrected_verdict(corrected_event)

    return corrected_verdict