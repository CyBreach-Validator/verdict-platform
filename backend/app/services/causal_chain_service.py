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
        .filter(Rule.rule_id == verdict.rule_id)
        .first()
    )

    if not rule:
        return None

    return {
        "rule": {
            "id": rule.id,
            "rule_id": rule.rule_id,
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
            # B6/N-D10: the column is `content_hash` in the v2.0 contract. This
            # read `verdict_hash`, which the schema no longer has, and it also
            # looked the rule up with `Rule.id == verdict.rule_id` -- an integer
            # column compared against a 64-character content hash, so the join
            # could never match and the whole endpoint 404'd on a valid verdict.
            "content_hash": verdict.content_hash,
            "causal_chain": verdict.causal_chain or [],
            "mttd_seconds": verdict.mttd_seconds,
            "matched_evidence_ref": verdict.matched_evidence_ref,
            "superseded": verdict.is_superseded,
        },
    }