import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.models.verdict import Verdict
from app.services.rule_detector import detect_rule_type
from app.services.rule_parser import parse_rule
from app.services.validator_service import validate_rule



def upload_sigma_rule(file_path: str, db: Session):
    """
    Uploads a Sigma rule, validates it,
    checks duplicates, and saves it to the database.
    """

    # Detect the rule type
    rule_type = detect_rule_type(file_path)

    if rule_type is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported rule type."
        )

    # Parse the Sigma rule
    rule_data = parse_rule(file_path)

    # Validate required fields
    required_fields = ["title", "description", "detection", "level"]

    for field in required_fields:
        if field not in rule_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    # Extract values
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

    # Check duplicate
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

    # Convert detection to JSON
    query = json.dumps(rule_data.get("detection"))

    # Save to database
   # Save to database
    new_rule = Rule(
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
    # Get rule
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id)
        .first()
    )

    if not rule:
        return None


    # Run validation
    validation_result = validate_rule(
        rule.query,
        event
    )


    # Extract only verdict status
    verdict_status = validation_result["status"]


    # Convert event dictionary to JSON
    event_json = json.dumps(event)


    # Save verdict
    verdict_record = Verdict(
        rule_id=rule.id,
        rule_name=rule.rule_name,
        verdict=verdict_status,
        event_data=event_json
    )


    db.add(verdict_record)
    db.commit()
    db.refresh(verdict_record)


    return {
        "rule_id": rule.id,
        "rule_name": rule.rule_name,
        "verdict": validation_result
    }
