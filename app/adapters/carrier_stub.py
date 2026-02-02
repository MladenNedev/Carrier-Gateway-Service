from __future__ import annotations

from app.adapters.base import AdapterResult, CarrierAdapter
from app.adapters.schemas import ExternalCarrierEvent
from app.domain.shipment import ShipmentStatus
from app.domain.shipment_event import ShipmentEventType


class MockCarrierAdapter(CarrierAdapter):
    _STATUS_MAP = {
        "IN_TRANSIT": ShipmentStatus.IN_TRANSIT,
        "DELIVERED": ShipmentStatus.DELIVERED,
        "FAILED": ShipmentStatus.FAILED,
    }

    _EVENT_MAP = {
        "IN_TRANSIT": ShipmentEventType.OUT_FOR_DELIVERY,
        "DELIVERED": ShipmentEventType.DELIVERED,
        "FAILED": ShipmentEventType.DELIVERY_FAILED,
    }

    async def ingest_event(self, payload: ExternalCarrierEvent) -> AdapterResult:
        status = self._STATUS_MAP.get(payload.event_code)
        event_type = self._EVENT_MAP.get(payload.event_code)
        if not event_type:
            raise ValueError(f"Unsupported event code: {payload.event_code}")

        return AdapterResult(
            merchant_id=payload.merchant_id,
            shipment_external_reference=payload.external_reference,
            event_type=event_type,
            occurred_at=payload.event_time,
            shipment_status=status,
        )
