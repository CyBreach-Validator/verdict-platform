from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.connector import ConnectorResponse
from app.security.security import get_current_user
from app.services.connector_service import (
    get_all_connectors,
    get_connector_by_id,
    seed_connectors,
)

# B11: the connector inventory was readable anonymously. It exposes which SIEMs
# are attached and their health, which is reconnaissance for an attacker
# targeting Delta's ingestion path, and `seed_connectors` is a write.
router = APIRouter(
    prefix="/connectors",
    tags=["SIEM Connectors"],
    dependencies=[Depends(get_current_user)],
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
