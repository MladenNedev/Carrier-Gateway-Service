"""lowercase shipment_status values

Revision ID: f2c9a7b6d3e1
Revises: e3b2c7d1f4a5
Create Date: 2026-02-01 12:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2c9a7b6d3e1"
down_revision: Union[str, Sequence[str], None] = "e3b2c7d1f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE shipment_status_new AS ENUM ("
        "'created', 'in_transit', 'delivered', 'failed', 'cancelled'"
        ")"
    )
    op.execute(
        "ALTER TABLE shipments "
        "ALTER COLUMN status TYPE shipment_status_new "
        "USING lower(status::text)::shipment_status_new"
    )
    op.execute("DROP TYPE shipment_status")
    op.execute("ALTER TYPE shipment_status_new RENAME TO shipment_status")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "CREATE TYPE shipment_status_new AS ENUM ("
        "'CREATED', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'CANCELLED'"
        ")"
    )
    op.execute(
        "ALTER TABLE shipments "
        "ALTER COLUMN status TYPE shipment_status_new "
        "USING upper(status::text)::shipment_status_new"
    )
    op.execute("DROP TYPE shipment_status")
    op.execute("ALTER TYPE shipment_status_new RENAME TO shipment_status")
