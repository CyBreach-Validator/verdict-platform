from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.models.verdict import Verdict
from app.utils.mitre import MITRE_TECHNIQUES



def get_detection_coverage(db: Session):

    coverage = defaultdict(
        lambda: {
            "rule_name": "",
            "detected": 0,
            "missed": 0,
            "partial": 0
        }
    )


    records = (
        db.query(Verdict, Rule)
        .join(
            Rule,
            Verdict.rule_id == Rule.id
        )
        .all()
    )


    for verdict, rule in records:

        technique = rule.mitre_technique


        coverage[technique]["rule_name"] = (
            rule.rule_name
        )


        if verdict.verdict == "Detected":
            coverage[technique]["detected"] += 1

        elif verdict.verdict == "Missed":
            coverage[technique]["missed"] += 1

        elif verdict.verdict == "Partial":
            coverage[technique]["partial"] += 1



    result = []


    for technique, data in coverage.items():

        if data["detected"] > data["missed"]:
            status = "Detected"

        elif data["partial"] > 0:
            status = "Partial"

        else:
            status = "Missed"


    result.append(
        {
            "technique": technique,

           "name": (
               MITRE_TECHNIQUES
               .get(technique, {})
               .get("name", "Unknown Technique")
            ),

           "tactic": (
               MITRE_TECHNIQUES
               .get(technique, {})
               .get("tactic", "Unknown")
            ),

            "rule_name": data["rule_name"],

            "status": status,

            "detected": data["detected"],
            "partial": data["partial"],
            "missed": data["missed"],
      }
    )

    return result

from app.models.audit_log import AuditLog


def get_revalidation_dashboard(db: Session):
    records = (
        db.query(AuditLog)
        .filter(AuditLog.action == "REVALIDATED")
        .order_by(AuditLog.created_at.asc())
        .all()
    )

    result = []

    for record in records:
        delta = 0
        improved = False
        gap_closed = False

        if record.details:
            try:
                import json

                details = json.loads(record.details)

                delta = details.get("delta", 0)
                improved = details.get("improved", False)
                gap_closed = details.get("gap_closed", False)

            except (TypeError, json.JSONDecodeError):
                pass

        result.append(
            {
                "id": record.id,
                "verdict_id": record.verdict_id,
                "related_verdict_id": record.related_verdict_id,
                "rule_id": record.rule_id,
                "rule_name": record.rule_name,
                "old_verdict": record.old_verdict,
                "new_verdict": record.new_verdict,
                "delta": delta,
                "improved": improved,
                "gap_closed": gap_closed,
                "verdict_hash": record.verdict_hash,
                "created_at": record.created_at,
            }
        )

    total = len(result)
    improved_count = sum(
        1 for item in result if item["improved"]
    )
    gap_closed_count = sum(
        1 for item in result if item["gap_closed"]
    )

    return {
        "total_revalidations": total,
        "improved": improved_count,
        "gap_closed": gap_closed_count,
        "history": result,
    }