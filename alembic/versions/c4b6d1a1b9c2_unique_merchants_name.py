"""add unique constraint on merchants.name

Revision ID: c4b6d1a1b9c2
Revises: b332e62ca5a8
Create Date: 2026-02-01 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4b6d1a1b9c2"
down_revision: Union[str, Sequence[str], None] = "b332e62ca5a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_merchants_name", "merchants", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_merchants_name", "merchants", type_="unique")
