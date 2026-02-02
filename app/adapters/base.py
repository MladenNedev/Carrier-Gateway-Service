from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.shipment import ShipmentStatus
from app.domain.shipment_event import ShipmentEventType


@dataclass(frozen=True)
class AdapterResult:
    merchant_id: UUID
    shipment_external_reference: str
    event_type: ShipmentEventType
    occurred_at: datetime
    shipment_status: ShipmentStatus | None = None
    reason: str | None = None


class CarrierAdapter(Protocol):
    async def ingest_event(self, payload: object) -> AdapterResult:
        """Translate external payload into internal adapter result."""
