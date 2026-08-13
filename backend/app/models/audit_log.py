from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.sql import func

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    action = Column(
        String(50),
        nullable=False
    )

    verdict_id = Column(
        Integer,
        nullable=False
    )

    related_verdict_id = Column(
        Integer,
        nullable=True
    )

    rule_id = Column(
        Integer,
        nullable=False
    )

    rule_name = Column(
        String,
        nullable=False
    )

    old_verdict = Column(
        String,
        nullable=True
    )

    new_verdict = Column(
        String,
        nullable=True
    )

    verdict_hash = Column(
        String(64),
        nullable=True
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )