from sqlalchemy import (
    JSON,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    text,
)
from sqlalchemy.sql import func

from app.database.database import Base


class Verdict(Base):
    __tablename__ = "verdict_events"

    # N-D13: at most one *current* verdict per contract hash. Superseded rows
    # are excluded so the correction/revalidation history can legitimately
    # repeat a hash. `postgresql_where` is intentionally not portable to
    # SQLite/MySQL, but PostgreSQL is the only supported datastore (the
    # DATABASE_URL is a postgresql+psycopg2 URL by construction).
    __table_args__ = (
        Index(
            "uq_verdict_events_content_hash_active",
            "content_hash",
            unique=True,
            postgresql_where=text("is_superseded = false"),
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Plan Section 9: `action_id` is the cross-pod join key for an evidence event.
    action_id = Column(String(64), nullable=False, index=True)

    # B6: `rule_id` is a string everywhere, keyed to the canonical
    # content-hash rule identifier owned by Pod Alpha, not an integer.
    rule_id = Column(String(64), ForeignKey("rules.rule_id"), nullable=False)

    rule_name = Column(String, nullable=False)

    verdict = Column(String, nullable=False)

    # B5: the plan's scale is 0.0-1.0 on every emit path.
    confidence = Column(Float, nullable=False, default=0.0)

    # M11: one causal-chain shape -- an ordered list of reasoning steps,
    # matching the frozen v2.0 schema's `array of string`.
    causal_chain = Column(JSON, nullable=False, default=list)

    mttd_seconds = Column(Float, nullable=True)

    matched_evidence_ref = Column(String(64), nullable=True)

    regulatory_control_refs = Column(JSON, nullable=False, default=list)

    event_data = Column(Text, nullable=False)

    # M12: one canonical hash field name, matching the wire contract.
    #
    # N-D13: uniqueness is PARTIAL (`WHERE is_superseded = false`), not global.
    # `content_hash` is computed from the seven contract fields, and the
    # revalidation/correction paths are deterministic, so re-validating an
    # unchanged verdict legitimately reproduces the *same* hash as the verdict
    # it supersedes. A global UNIQUE would reject that insert and break the
    # revalidate endpoint outright. Constraining only the current (non-
    # superseded) rows still catches the real failure mode -- the same verdict
    # being double-written -- while leaving the audit history intact.
    content_hash = Column(String(64), nullable=False, index=True)

    is_superseded = Column(
        Boolean,
        default=False,
        nullable=False
    )

    superseded_by = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
