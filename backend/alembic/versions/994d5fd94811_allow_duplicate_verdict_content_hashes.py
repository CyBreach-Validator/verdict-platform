"""allow duplicate verdict content hashes

Revision ID: 994d5fd94811
Revises: 30f49886e5e2
Create Date: 2026-09-26 21:03:01.310923

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "994d5fd94811"
down_revision: Union[str, Sequence[str], None] = "30f49886e5e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint from verdict_hash."""

    op.execute("""
        ALTER TABLE verdict_events
        DROP CONSTRAINT IF EXISTS verdict_events_verdict_hash_key
    """)


def downgrade() -> None:
    """Restore unique constraint if duplicate hashes do not exist."""

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'verdict_events_verdict_hash_key'
                  AND conrelid = 'verdict_events'::regclass
            ) THEN

                IF EXISTS (
                    SELECT verdict_hash
                    FROM verdict_events
                    GROUP BY verdict_hash
                    HAVING COUNT(*) > 1
                ) THEN
                    RAISE EXCEPTION
                        'Cannot restore unique constraint: duplicate verdict_hash values exist';
                END IF;

                ALTER TABLE verdict_events
                ADD CONSTRAINT verdict_events_verdict_hash_key
                UNIQUE (verdict_hash);
            END IF;
        END
        $$;
    """)