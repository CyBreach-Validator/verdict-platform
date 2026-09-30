from sqlalchemy.orm import Session

from app.models.connector import Connector


def _canonical_connectors_notice() -> dict:
    return {
        "owner": "alpha",
        "registry": "/api/v2/connectors",
        "canonical_table": "connectors",
        "status": "canonical_registry",
        "note": (
            "Delta keeps a local dashboard-only health view, but the authoritative "
            "connector registry is owned by Alpha."
        ),
    }


def get_all_connectors(db: Session):
    """
    Return all registered SIEM connectors.

    The canonical registry for connector registration and health lives in Alpha.
    Delta retains a local dashboard view for UI convenience, but it must not be
    treated as the source of truth.
    """
    try:
        import os
        from urllib import request, error

        alpha_base = os.getenv("ALPHA_CONNECTOR_REGISTRY_URL", "http://rule-ingestion:8001")
        alpha_url = f"{alpha_base}/api/v2/connectors/health"
        req = request.Request(alpha_url, method="GET")
        with request.urlopen(req, timeout=3) as resp:
            payload = resp.read().decode("utf-8")
            if payload:
                import json
                parsed = json.loads(payload)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict) and isinstance(parsed.get("connectors"), list):
                    return parsed["connectors"]
    except (error.URLError, ValueError, TimeoutError):
        pass

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
