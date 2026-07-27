import json

from sqlalchemy.orm import Session

from app.models.verdict import Verdict
from app.utils.hash_utils import generate_verdict_hash
from app.kafka.producer import publish_corrected_verdict


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


def get_verdict_by_id(
    db: Session,
    verdict_id: int
):
    return (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )


def get_verdicts_by_rule(
    db: Session,
    rule_id: int
):
    return (
        db.query(Verdict)
        .filter(Verdict.rule_id == rule_id)
        .all()
    )


def correct_verdict(
    db: Session,
    verdict_id: int,
    new_verdict: str
):
    """
    Creates a corrected verdict while preserving
    the original verdict.
    """

    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None

    new_hash = generate_verdict_hash(
        rule_id=old_verdict.rule_id,
        rule_name=old_verdict.rule_name,
        verdict=new_verdict,
        event_data=json.loads(old_verdict.event_data)
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

    publish_corrected_verdict(
        {
            "id": corrected_verdict.id,
            "rule_id": corrected_verdict.rule_id,
            "rule_name": corrected_verdict.rule_name,
            "verdict": corrected_verdict.verdict,
            "verdict_hash": corrected_verdict.verdict_hash,
            "supersedes": old_verdict.id
        }
    )

    return corrected_verdict