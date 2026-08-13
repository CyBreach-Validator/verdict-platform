from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.rule import Rule
from app.models.verdict import Verdict
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import (
    get_detection_coverage,
    get_revalidation_dashboard,
)

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Total rules
    total_rules = db.query(Rule).count()

    # Total verdicts
    total_verdicts = db.query(Verdict).count()

    # Total detected
    detected = (
        db.query(Verdict)
        .filter(Verdict.verdict == "Detected")
        .count()
    )

    # Total missed
    missed = (
        db.query(Verdict)
        .filter(Verdict.verdict == "Missed")
        .count()
    )

    return DashboardStats(
        total_rules=total_rules,
        total_verdicts=total_verdicts,
        detected=detected,
        missed=missed
    )

@router.get("/dashboard/coverage")
def dashboard_coverage(db: Session = Depends(get_db)):
    return get_detection_coverage(db)

@router.get("/dashboard/revalidation")
def dashboard_revalidation(
    db: Session = Depends(get_db)
):
    return get_revalidation_dashboard(db)