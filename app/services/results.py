from dataclasses import dataclass

from app.domain.shipment import Shipment


@dataclass
class ShipmentCreateResponse:
    shipment: Shipment
    created: bool
