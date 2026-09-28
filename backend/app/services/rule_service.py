import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.models.verdict import Verdict
from app.services.rule_detector import detect_rule_type
from app.services.rule_parser import parse_rule
from app.services.validator_service import validate_rule
from app.services.verdict_service import save_verdict
from app.utils.rule_hash_utils import compute_rule_id


def upload_sigma_rule(file_path: str, db: Session):
    """
    Uploads a Sigma rule, validates it,
    checks duplicates, and saves it to the database.
    """

    rule_type = detect_rule_type(file_path)

    if rule_type is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported rule type."
        )

    rule_data = parse_rule(file_path)

    required_fields = ["title", "description", "detection", "level"]

    for field in required_fields:
        if field not in rule_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    rule_name = rule_data.get("title")
    description = rule_data.get("description")
    severity = rule_data.get("level")
    status = rule_data.get("status")

    tags = rule_data.get("tags", [])
    mitre_technique = None

    for tag in tags:
        if tag.startswith("attack.t"):
            mitre_technique = tag.replace("attack.", "").upper()
            break

    existing_rule = (
        db.query(Rule)
        .filter(Rule.rule_name == rule_name)
        .first()
    )

    if existing_rule:
        raise HTTPException(
            status_code=409,
            detail="Rule with this name already exists."
        )

    query = json.dumps(rule_data.get("detection"))

    new_rule = Rule(
        # B6: assign the canonical content hash at creation. Without it this
        # row has `rule_id IS NULL`, so no verdict produced from it can be
        # joined to a rule on another pod -- the whole point of the shared
        # identifier. `compute_rule_id` is the same digest Pod Alpha derives, so
        # an identical rule ingested from both sides collapses to one id.
        rule_id=compute_rule_id(
            rule_name=rule_name,
            query=query,
            rule_type=rule_type,
            mitre_technique=mitre_technique,
        ),
        rule_name=rule_name,
        rule_type=rule_type,
        severity=severity,
        description=description,
        query=query,
        status=status,
        mitre_technique=mitre_technique
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return new_rule


def get_all_rules(db: Session):
    return db.query(Rule).all()


def get_rule_by_id(db: Session, rule_id: int):
    return (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )


def create_rule(db: Session, rule):
    new_rule = Rule(
        # B6: same reasoning as `upload_sigma_rule` -- the canonical id is part
        # of creating the rule, not an optional annotation filled in later.
        rule_id=compute_rule_id(
            rule_name=rule.rule_name,
            query=rule.query,
            rule_type=rule.rule_type,
            mitre_technique=rule.mitre_technique,
        ),
        rule_name=rule.rule_name,
        rule_type=rule.rule_type,
        severity=rule.severity,
        description=rule.description,
        query=rule.query,
        status=rule.status,
        mitre_technique=rule.mitre_technique
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return new_rule


def update_rule(
    db: Session,
    rule_id: int,
    updated_rule
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None

    rule.rule_name = updated_rule.rule_name
    rule.rule_type = updated_rule.rule_type
    rule.severity = updated_rule.severity
    rule.description = updated_rule.description
    rule.query = updated_rule.query
    rule.status = updated_rule.status
    rule.mitre_technique = updated_rule.mitre_technique

    db.commit()
    db.refresh(rule)

    return rule


def delete_rule(
    db: Session,
    rule_id: int
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return False

    db.delete(rule)
    db.commit()

    return True


def validate_uploaded_rule(
    db: Session,
    rule_id: int,
    event: dict
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None

    validation_result = validate_rule(
        rule.query,
        event
    )

    verdict_status = validation_result["status"]

    # B6/N-D11: this built a Verdict row by hand with `rule_id=rule.id` -- Delta's
    # local integer surrogate, not the canonical content hash every other pod
    # uses -- and with a `verdict_hash` column that the v2.0 schema does not
    # have. A verdict produced here could not be joined to a rule on any other
    # pod, and the write itself would have failed. Go through `save_verdict` so
    # the row, its `content_hash` and the canonical payload are produced by the
    # one serializer.
    action_id = str(
        event.get("action_id")
        or event.get("event_id")
        or f"rule-{rule.rule_id}"
    )

    verdict_record, payload = save_verdict(
        db=db,
        action_id=action_id,
        rule_id=rule.rule_id,
        rule_name=rule.rule_name,
        verdict=verdict_status,
        confidence=validation_result["confidence"],
        event=event,
        causal_chain=validation_result["causal_chain"],
        mttd_seconds=validation_result["mttd_seconds"],
        matched_evidence_ref=validation_result["matched_evidence_ref"],
        regulatory_control_refs=rule.regulatory_control_refs or [],
    )

    return {
        "rule_id": rule.rule_id,
        "rule_name": rule.rule_name,
        "verdict_id": verdict_record.id,
        "verdict": validation_result,
        "verdict_event": payload,
    }


def submit_rule_for_approval(
    db: Session,
    rule_id: int
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None, "Rule not found"

    if rule.status not in ["Draft", "Rejected"]:
        return None, (
            f"Rule cannot be submitted from "
            f"'{rule.status}' status."
        )

    rule.status = "Pending"

    db.commit()
    db.refresh(rule)

    return rule, None


def approve_rule(
    db: Session,
    rule_id: int
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None, "Rule not found"

    if rule.status != "Pending":
        return None, (
            f"Only Pending rules can be approved. "
            f"Current status: '{rule.status}'."
        )

    rule.status = "Approved"

    db.commit()
    db.refresh(rule)

    return rule, None


def reject_rule(
    db: Session,
    rule_id: int
):
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None, "Rule not found"

    if rule.status != "Pending":
        return None, (
            f"Only Pending rules can be rejected. "
            f"Current status: '{rule.status}'."
        )

    rule.status = "Rejected"

    db.commit()
    db.refresh(rule)

    return rule, None