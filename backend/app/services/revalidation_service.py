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


def revalidate_verdict(db: Session, verdict_id: int):
    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None

    rule = (
        db.query(Rule)
        .filter(Rule.id == old_verdict.rule_id)
        .first()
    )

    if not rule:
        return None

    event = json.loads(old_verdict.event_data)

    validation_result = validate_rule(
        rule.query,
        event
    )

    new_verdict_status = validation_result["status"]

    new_hash = generate_verdict_hash(
        rule_id=rule.id,
        rule_name=rule.rule_name,
        verdict=new_verdict_status,
        event_data=event
    )

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

    old_verdict.is_superseded = True
    old_verdict.superseded_by = new_verdict.id

    db.commit()
    db.refresh(old_verdict)

    action_id = str(
        event.get("action_id", new_verdict.id)
    )

    confidence = {
        "Detected": 1.0,
        "Partial": 0.5,
        "Missed": 0.0,
        "NoData": 0.0,
        "No Data": 0.0
    }.get(new_verdict.verdict, 0.0)

    corrected_event = {
        "action_id": action_id,
        "verdict": new_verdict.verdict,
        "confidence": confidence,
        "causal_chain": validation_result.get(
            "matched_fields", []
        ),
        "mttd_seconds": None,
        "matched_evidence_ref": action_id,
        "regulatory_control_refs": [],
        "content_hash": new_verdict.verdict_hash
    }

    print("Publishing corrected verdict to Kafka...")

    publish_corrected_verdict(corrected_event)

    gap_closed = (
        old_verdict.verdict == "Missed"
        and new_verdict.verdict == "Detected"
    )

    if gap_closed:
        gap_closed_event = {
            "action_id": action_id,
            "verdict": new_verdict.verdict,
            "confidence": confidence,
            "causal_chain": validation_result.get(
                "matched_fields", []
            ),
            "mttd_seconds": None,
            "matched_evidence_ref": action_id,
            "regulatory_control_refs": [],
            "content_hash": new_verdict.verdict_hash
        }

        publish_gap_closed_event(gap_closed_event)

        print("✅ Gap-closed event published")

    create_audit_log(
        db=db,
        action="REVALIDATION",
        entity_type="verdict",
        entity_id=new_verdict.id,
        details={
            "previous_verdict_id": old_verdict.id,
            "old_verdict": old_verdict.verdict,
            "new_verdict": new_verdict.verdict,
            "gap_closed": gap_closed
        }
    )

    return {
        "verdict_id": new_verdict.id,
        "previous_verdict_id": old_verdict.id,
        "old_verdict": old_verdict.verdict,
        "new_verdict": new_verdict.verdict,
        "gap_closed": gap_closed,
        "content_hash": new_verdict.verdict_hash
    }