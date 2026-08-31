from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.security.security import get_current_user

import os
import shutil

from app.database.database import get_db
from app.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from app.schemas.validator import ValidationRequest
from app.models.rule import Rule

from app.services.rule_service import (
    upload_sigma_rule,
    get_all_rules,
    get_rule_by_id,
    create_rule as create_rule_service,
    update_rule as update_rule_service,
    delete_rule as delete_rule_service,
    validate_uploaded_rule,
    submit_rule_for_approval,
    approve_rule as approve_rule_service,
    reject_rule as reject_rule_service,
)

router = APIRouter()


@router.post("/rules", response_model=RuleResponse)
def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return create_rule_service(db, rule)


@router.get("/rules", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db),
current_user: str = Depends(get_current_user)
):
    return get_all_rules(db)

@router.get("/rules/search")
def search_rules(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    all_rules = db.query(Rule).all()

    print("========== SEARCH DEBUG ==========")
    print("Query:", q)
    print("Total rules:", len(all_rules))

    for rule in all_rules:
        print(rule.id, rule.rule_name)

    results = (
        db.query(Rule)
        .filter(Rule.rule_name.ilike(f"%{q}%"))
        .all()
    )

    print("Matched:", len(results))
    print("==================================")

    return results

@router.get("/rules/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    rule = get_rule_by_id(db, rule_id)

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Rule not found"
        )

    return rule


@router.put("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    updated_rule: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    rule = update_rule_service(
        db,
        rule_id,
        updated_rule
    )

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Rule not found"
        )

    return rule

@router.put("/rules/{rule_id}/submit")
def submit_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rule, error = submit_rule_for_approval(
        db,
        rule_id
    )

    if error:
        status_code = 404 if error == "Rule not found" else 400

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return rule


@router.put("/rules/{rule_id}/approve")
def approve_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rule, error = approve_rule_service(
        db,
        rule_id
    )

    if error:
        status_code = 404 if error == "Rule not found" else 400

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return rule


@router.put("/rules/{rule_id}/reject")
def reject_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rule, error = reject_rule_service(
        db,
        rule_id
    )

    if error:
        status_code = 404 if error == "Rule not found" else 400

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return rule

@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    deleted = delete_rule_service(
        db,
        rule_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Rule not found"
        )

    return {
        "message": "Rule deleted successfully"
    }


@router.post("/rules/upload")
def upload_rule(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    upload_folder = "uploads"

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(
        upload_folder,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    new_rule = upload_sigma_rule(
        file_path,
        db
    )

    return {
        "message": "Rule uploaded and saved successfully",
        "rule_id": new_rule.id,
        "rule_name": new_rule.rule_name
    }


@router.post("/rules/validate/{rule_id}")
def validate_rule_endpoint(
    rule_id: int,
    request: ValidationRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    result = validate_uploaded_rule(
        db=db,
        rule_id=rule_id,
        event=request.event
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Rule not found."
        )

    return result
    

@router.get("/rules/{rule_id}/compare")
def compare_rule(rule_id: int, db: Session = Depends(get_db)):
    current = db.query(Rule).filter(Rule.id == rule_id).first()

    if not current:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Temporary demo data
    proposed = {
        "title": "Suspicious PowerShell",
        "query": 'Image="powershell.exe" AND Parent="cmd.exe"',
        "severity": "High",
        "status": "Pending"
    }

    return {
    "current": {
        "title": current.rule_name,
        "query": current.query,
        "severity": current.severity,
        "status": current.status,
    },
    "proposed": proposed,
}