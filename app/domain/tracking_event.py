from dataclasses import dataclass
from uuid import UUID
from enum import Enum

from app.domain.shipment import Shipment

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
    event_type: ShipmentEventType
    event_source: ShipmentEventSource