from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.connector import ConnectorResponse
from app.services.connector_service import (
    get_all_connectors,
    get_connector_by_id,
    seed_connectors,
)

router = APIRouter(
    prefix="/connectors",
    tags=["SIEM Connectors"],
)


@router.get("", response_model=list[ConnectorResponse])
def list_connectors(db: Session = Depends(get_db)):
    return get_all_connectors(db)


@router.get("/{connector_id}", response_model=ConnectorResponse)
def connector_details(
    connector_id: int,
    db: Session = Depends(get_db),
):
    connector = get_connector_by_id(connector_id, db)

    if connector is None:
        raise HTTPException(
            status_code=404,
            detail="Connector not found",
        )

    return connector
