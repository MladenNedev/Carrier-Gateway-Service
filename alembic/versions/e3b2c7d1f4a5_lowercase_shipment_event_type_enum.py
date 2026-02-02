"""lowercase shipment_event_type values

Revision ID: e3b2c7d1f4a5
Revises: d1a4c8c7b6e9
Create Date: 2026-02-01 12:20:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3b2c7d1f4a5"
down_revision: Union[str, Sequence[str], None] = "d1a4c8c7b6e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE shipment_event_type_new AS ENUM ("
        "'label_created', 'picked_up', 'out_for_delivery', 'delivered', 'delivery_failed'"
        ")"
    )
    op.execute(
        "ALTER TABLE shipment_events "
        "ALTER COLUMN type TYPE shipment_event_type_new "
        "USING lower(type::text)::shipment_event_type_new"
    )
    op.execute("DROP TYPE shipment_event_type")
    op.execute("ALTER TYPE shipment_event_type_new RENAME TO shipment_event_type")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "CREATE TYPE shipment_event_type_new AS ENUM ("
        "'LABEL_CREATED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED', 'DELIVERY_FAILED'"
        ")"
    )
    op.execute(
        "ALTER TABLE shipment_events "
        "ALTER COLUMN type TYPE shipment_event_type_new "
        "USING upper(type::text)::shipment_event_type_new"
    )
    op.execute("DROP TYPE shipment_event_type")
    op.execute("ALTER TYPE shipment_event_type_new RENAME TO shipment_event_type")
