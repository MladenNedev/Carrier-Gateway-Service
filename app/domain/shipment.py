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


ALLOWED_TRANSITIONS = {
    ShipmentStatus.CREATED: {ShipmentStatus.IN_TRANSIT, ShipmentStatus.CANCELLED},
    ShipmentStatus.IN_TRANSIT: {
        ShipmentStatus.DELIVERED,
        ShipmentStatus.FAILED,
        ShipmentStatus.CANCELLED,
    },
    ShipmentStatus.DELIVERED: set(),
    ShipmentStatus.FAILED: set(),
    ShipmentStatus.CANCELLED: set(),
}


def can_transition(current: ShipmentStatus, target: ShipmentStatus) -> bool:
    if current == target:
        return True
    return target in ALLOWED_TRANSITIONS.get(current, set())
