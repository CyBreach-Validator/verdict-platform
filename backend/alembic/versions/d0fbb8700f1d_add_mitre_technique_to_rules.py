"""add mitre technique to rules

Revision ID: d0fbb8700f1d
Revises: 072d157c3cab
Create Date: 2026-07-24 16:47:31.007627

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0fbb8700f1d'
down_revision: Union[str, Sequence[str], None] = '072d157c3cab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'rules',
        sa.Column(
            'mitre_technique',
            sa.String(length=20),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'rules',
        'mitre_technique'
    )