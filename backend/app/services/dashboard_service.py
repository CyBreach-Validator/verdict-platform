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

                "name":
                MITRE_TECHNIQUES
                .get(
                    technique,
                    {}
                )
                .get(
                    "name",
                    "Unknown Technique"
                ),

                "tactic":
                MITRE_TECHNIQUES
                .get(
                    technique,
                    {}
                )
                .get(
                    "tactic",
                    "Unknown"
                ),

                "rule_name":
                data["rule_name"],

                "status": status
            }
        )


    return result