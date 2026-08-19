import json

from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.models.verdict import Verdict
from app.services.validator_service import validate_rule
from app.utils.hash_utils import generate_verdict_hash
from app.kafka.producer import (
    publish_corrected_verdict,
    publish_gap_closed_event
)
from app.services.audit_log_service import create_audit_log


def revalidate_verdict(
    db: Session,
    verdict_id: int
):
    """
    Re-run the rule associated with an existing verdict
    against the original event data.

    The original verdict is preserved.
    A new verdict record is created for the re-validation result.
    """

    # Get the original verdict
    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None

    # Get the associated rule
    rule = (
        db.query(Rule)
        .filter(Rule.id == old_verdict.rule_id)
        .first()
    )

    if not rule:
        return None

    # Recover the original event
    event = json.loads(old_verdict.event_data)

    # Re-run the detection rule
    validation_result = validate_rule(
        rule.query,
        event
    )

    new_verdict_status = validation_result["status"]

    # Generate hash for the new verdict
    new_hash = generate_verdict_hash(
        rule_id=rule.id,
        rule_name=rule.rule_name,
        verdict=new_verdict_status,
        event_data=event
    )

    # Create new verdict record
    new_verdict = Verdict(
        rule_id=rule.id,
        rule_name=rule.rule_name,
        verdict=new_verdict_status,
        event_data=json.dumps(event),
        verdict_hash=new_hash,
        is_superseded=False,
        superseded_by=None
    )

    db.add(new_verdict)
    db.commit()
    db.refresh(new_verdict)

    # Preserve the old verdict but mark it superseded
    old_verdict.is_superseded = True
    old_verdict.superseded_by = new_verdict.id

    db.commit()
    db.refresh(old_verdict)

    # Publish re-validation result
    publish_corrected_verdict(
        {
            "id": new_verdict.id,
            "rule_id": new_verdict.rule_id,
            "rule_name": new_verdict.rule_name,
            "verdict": new_verdict.verdict,
            "verdict_hash": new_verdict.verdict_hash,
            "supersedes": old_verdict.id,
            "revalidation": True
        }
    )

    verdict_scores = {
        "Missed": 0,
        "Partial": 1,
        "Detected": 2,
        "No Data": 0
    }

    old_score = verdict_scores.get(
        old_verdict.verdict,
        0
    )

    new_score = verdict_scores.get(
        new_verdict.verdict,
        0
    )

    delta = new_score - old_score

    improved = delta > 0

    gap_closed = (
        old_verdict.verdict == "Missed"
        and new_verdict.verdict == "Detected"
    )

    # Publish dedicated gap-closed event
    if gap_closed:
        publish_gap_closed_event(
            {
                "event_type": "GAP_CLOSED",
                "verdict_id": new_verdict.id,
                "previous_verdict_id": old_verdict.id,
                "rule_id": rule.id,
                "rule_name": rule.rule_name,
                "old_verdict": old_verdict.verdict,
                "new_verdict": new_verdict.verdict,
                "verdict_hash": new_verdict.verdict_hash,
                "supersedes": old_verdict.id,
                "revalidation": True,
                "gap_closed": True
            }
        )

    create_audit_log(
        db=db,
        action="REVALIDATED",
        verdict_id=new_verdict.id,
        related_verdict_id=old_verdict.id,
        rule_id=rule.id,
        rule_name=rule.rule_name,
        old_verdict=old_verdict.verdict,
        new_verdict=new_verdict.verdict,
        verdict_hash=new_verdict.verdict_hash,
        details={
            "delta": delta,
            "improved": improved,
            "gap_closed": gap_closed,
            "revalidation": True,
        },
    )

    return {
        "old_verdict": {
            "id": old_verdict.id,
            "verdict": old_verdict.verdict,
            "verdict_hash": old_verdict.verdict_hash,
            "created_at": old_verdict.created_at
        },
        "new_verdict": {
            "id": new_verdict.id,
            "verdict": new_verdict.verdict,
            "verdict_hash": new_verdict.verdict_hash,
            "created_at": new_verdict.created_at
        },
        "rule": {
            "id": rule.id,
            "name": rule.rule_name
        },
        "validation": validation_result,
        "comparison": {
            "old_score": old_score,
            "new_score": new_score,
            "delta": delta,
            "improved": improved,
            "gap_closed": gap_closed
        }
    }