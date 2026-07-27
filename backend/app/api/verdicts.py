from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.verdict import VerdictResponse
from app.security.security import get_current_user

from app.services.verdict_service import (
    get_all_verdicts,
    get_verdict_by_id,
    get_verdicts_by_rule as get_verdicts_by_rule_service,
)
from app.schemas.verdict_correction import (
    VerdictCorrectionRequest,
    VerdictCorrectionResponse,
)

from app.services.verdict_service import correct_verdict
from app.schemas.causal_chain import CausalChainResponse
from app.services.causal_chain_service import get_causal_chain

router = APIRouter()


@router.get("/verdicts", response_model=list[VerdictResponse])
def get_verdicts(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return get_all_verdicts(db)


@router.get("/verdicts/{verdict_id}", response_model=VerdictResponse)
def get_verdict(
    verdict_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    verdict = get_verdict_by_id(db, verdict_id)

    if not verdict:
        raise HTTPException(
            status_code=404,
            detail="Verdict not found."
        )

    return verdict


@router.get("/verdicts/rule/{rule_id}", response_model=list[VerdictResponse])
def get_verdicts_by_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    verdicts = get_verdicts_by_rule_service(db, rule_id)

    if not verdicts:
        raise HTTPException(
            status_code=404,
            detail="No verdicts found for this rule."
        )

    return verdicts


@router.put(
    "/verdicts/{verdict_id}/correct",
    response_model=VerdictCorrectionResponse
)
def correct_verdict_endpoint(
    verdict_id: int,
    request: VerdictCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    verdict = correct_verdict(
        db=db,
        verdict_id=verdict_id,
        new_verdict=request.verdict
    )

    if not verdict:
        raise HTTPException(
            status_code=404,
            detail="Verdict not found."
        )

    return verdict

@router.get(
    "/verdicts/{verdict_id}/chain",
    response_model=CausalChainResponse
)
def verdict_chain(
    verdict_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    chain = get_causal_chain(
        db,
        verdict_id
    )

    if not chain:
        raise HTTPException(
            status_code=404,
            detail="Verdict not found"
        )

    return chain