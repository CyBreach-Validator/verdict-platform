"""create missing current tables

Revision ID: 30f49886e5e2
Revises: fa0be04e9958
Create Date: 2026-09-26 19:03:57.863940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30f49886e5e2'
down_revision: Union[str, Sequence[str], None] = 'fa0be04e9958'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create missing current application tables."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "connectors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=True),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_connectors_id", "connectors", ["id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("verdict_id", sa.Integer(), nullable=False),
        sa.Column("related_verdict_id", sa.Integer(), nullable=True),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column("old_verdict", sa.String(), nullable=True),
        sa.Column("new_verdict", sa.String(), nullable=True),
        sa.Column("verdict_hash", sa.String(length=64), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)


def downgrade() -> None:
    """Remove the tables created by this migration."""

    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_connectors_id", table_name="connectors")
    op.drop_table("connectors")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")