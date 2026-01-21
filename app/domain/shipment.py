from dataclasses import dataclass
from enum import Enum
from uuid import UUID

class ShipmentStatus(str, Enum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Shipment:
    id: UUID
    merchant_id: UUID
    name: str
    external_reference: str | None
    status: ShipmentStatus