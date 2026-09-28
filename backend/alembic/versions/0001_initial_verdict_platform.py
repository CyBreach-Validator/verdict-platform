"""create verdict platform schema

Baseline migration for the CyBreach Verdict Platform (Pod Delta).

This replaces a ten-revision chain that could never run on an empty database:
no revision created `verdict_events` (the base only ALTERed it), one added a
column to a table named `verdicts` that nothing ever created, two were chained
no-ops, and the head dropped a unique constraint on a column that was never
added. `Base.metadata.create_all()` masked all of this at runtime, so the two
schema sources silently disagreed.

This revision is the single source of truth and is generated to match
`app/models/*.py` exactly. It creates the plan v2.0 verdict contract columns
up front, so no follow-up ALTERs are needed.

Revision ID: 0001_initial_verdict_platform
Revises:
Create Date: 2026-09-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_verdict_platform"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the full application schema."""

    # --- users -------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    # --- rules -------------------------------------------------------------
    # `rule_id` is the canonical content-hash identifier shared across pods
    # (B6); `id` remains the local surrogate key for Delta's own routes.
    op.create_table(
        "rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.String(length=64), nullable=True),
        sa.Column("rule_name", sa.String(length=200), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("mitre_technique", sa.String(length=20), nullable=True),
        sa.Column(
            "regulatory_control_refs",
            sa.JSON(),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rules_id", "rules", ["id"], unique=False)
    op.create_index("ix_rules_rule_id", "rules", ["rule_id"], unique=True)

    # --- verdict_events ----------------------------------------------------
    # Mirrors app/models/verdict.py: the plan's v2.0 verdict contract, with
    # `content_hash` as the single canonical hash field name.
    op.create_table(
        "verdict_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("action_id", sa.String(length=64), nullable=False),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column("verdict", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "causal_chain",
            sa.JSON(),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
        sa.Column("mttd_seconds", sa.Float(), nullable=True),
        sa.Column("matched_evidence_ref", sa.String(length=64), nullable=True),
        sa.Column(
            "regulatory_control_refs",
            sa.JSON(),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
        sa.Column("event_data", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "is_superseded",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("superseded_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["rule_id"],
            ["rules.rule_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_verdict_events_id", "verdict_events", ["id"], unique=False
    )
    op.create_index(
        "ix_verdict_events_action_id",
        "verdict_events",
        ["action_id"],
        unique=False,
    )
    op.create_index(
        "ix_verdict_events_content_hash",
        "verdict_events",
        ["content_hash"],
        unique=False,
    )
    # N-D13: restore duplicate detection as a PARTIAL unique index rather than
    # a global one. `content_hash` covers the seven contract fields, and the
    # revalidate/correct paths are deterministic, so re-validating an unchanged
    # verdict reproduces the same hash as the row it supersedes. A global
    # UNIQUE would reject that insert and break `POST /verdicts/{id}/revalidate`
    # outright. Only current (non-superseded) rows are constrained, which still
    # blocks the real failure mode -- the same verdict being double-written --
    # while preserving the correction history.
    op.create_index(
        "uq_verdict_events_content_hash_active",
        "verdict_events",
        ["content_hash"],
        unique=True,
        postgresql_where=sa.text("is_superseded = false"),
    )

    # --- audit_logs --------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("verdict_id", sa.Integer(), nullable=False),
        sa.Column("related_verdict_id", sa.Integer(), nullable=True),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column("old_verdict", sa.String(), nullable=True),
        sa.Column("new_verdict", sa.String(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)

    # --- platform_connector_health ----------------------------------------
    # N-D12: this used to be a table named `connectors`, which collides with
    # the one Pod Gamma creates and the one Pod Alpha owns as the canonical
    # Connector Framework registry (plan Section 7). Delta only stores health
    # metadata for its dashboard, so it gets its own namespace.
    op.create_table(
        "platform_connector_health",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_platform_connector_health_id",
        "platform_connector_health",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the full application schema."""

    op.drop_index("ix_platform_connector_health_id", table_name="platform_connector_health")
    op.drop_table("platform_connector_health")

    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("uq_verdict_events_content_hash_active", table_name="verdict_events")
    op.drop_index("ix_verdict_events_content_hash", table_name="verdict_events")
    op.drop_index("ix_verdict_events_action_id", table_name="verdict_events")
    op.drop_index("ix_verdict_events_id", table_name="verdict_events")
    op.drop_table("verdict_events")

    op.drop_index("ix_rules_rule_id", table_name="rules")
    op.drop_index("ix_rules_id", table_name="rules")
    op.drop_table("rules")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
