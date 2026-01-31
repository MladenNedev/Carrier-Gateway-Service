from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

class ShipmentEventType(str, Enum):
    LABEL_CREATED = "label_created"
    PICKED_UP = "picked_up"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELIVERY_FAILED = "DELIVERY_FAILED"

class ShipmentEventSource(str, Enum):
    CARRIER = "carrier"
    SYSTEM = "system"
    MANUAL = "manual"


@dataclass
class ShipmentTrackingEvent:
    id: UUID
    shipment_id: UUID
    type: ShipmentEventType
    source: ShipmentEventSource
    reason: str | None
    occurred_at: datetime
