from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.security.security import get_current_user
from app.services.audit_log_service import (
    get_all_audit_logs,
    get_audit_log_by_id,
    verify_verdict_immutability,
)


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return get_all_audit_logs(db)


@router.get("/verify/{verdict_id}")
def verify_verdict(
    verdict_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = verify_verdict_immutability(
        db,
        verdict_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Verdict not found.",
        )

    return result


@router.get("/{audit_log_id}")
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    audit_log = get_audit_log_by_id(
        db,
        audit_log_id
    )

    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found.",
        )

    return audit_log