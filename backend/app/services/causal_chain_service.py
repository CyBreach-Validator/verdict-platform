import json

from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.models.verdict import Verdict


def get_causal_chain(
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

    rule = (
        db.query(Rule)
        .filter(Rule.id == verdict.rule_id)
        .first()
    )

    if not rule:
        return None

    return {
        "rule": {
            "id": rule.id,
            "name": rule.rule_name,
            "technique": rule.mitre_technique,
        },
        "event": json.loads(verdict.event_data),
        "validation": {
            "status": (
                "Matched"
                if verdict.verdict == "Detected"
                else "Not Matched"
            )
        },
        "classifier": {
            "status": verdict.verdict
        },
        "verdict": {
            "id": verdict.id,
            "hash": verdict.verdict_hash,
            "superseded": verdict.is_superseded,
        },
    }