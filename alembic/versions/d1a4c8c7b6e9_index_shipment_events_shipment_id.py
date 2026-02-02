"""index shipment_events shipment_id

Revision ID: d1a4c8c7b6e9
Revises: c4b6d1a1b9c2
Create Date: 2026-02-01 12:10:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1a4c8c7b6e9"
down_revision: Union[str, Sequence[str], None] = "c4b6d1a1b9c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_shipment_events_shipment_id", "shipment_events", ["shipment_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_shipment_events_shipment_id", table_name="shipment_events")
