from sqlalchemy.orm import Session

from app.models.connector import Connector


def get_all_connectors(db: Session):
    """
    Return all registered SIEM connectors.
    """
    return db.query(Connector).order_by(Connector.name).all()


def get_connector_by_id(connector_id: int, db: Session):
    """
    Return a single connector by ID.
    """
    return (
        db.query(Connector)
        .filter(Connector.id == connector_id)
        .first()
    )

def seed_connectors(db: Session):
    """
    Insert sample SIEM connectors if the table is empty.
    """

    if db.query(Connector).count() > 0:
        return

    connectors = [
        Connector(
            name="Splunk",
            status="Healthy",
            version="9.3",
        ),
        Connector(
            name="Microsoft Sentinel",
            status="Healthy",
            version="1.4",
        ),
        Connector(
            name="IBM QRadar",
            status="Disconnected",
            version="7.5",
        ),
        Connector(
            name="Elastic",
            status="Connecting",
            version="8.11",
        ),
    ]

    db.add_all(connectors)
    db.commit()