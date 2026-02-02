from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.shipment_event import ShipmentEventSource, ShipmentEventType
from app.schemas.shipments import ShipmentResponse


class ShipmentEventCreate(BaseModel):
    type: ShipmentEventType
    source: ShipmentEventSource
    reason: str | None = None
    occurred_at: datetime | None = None


class ShipmentEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shipment_id: UUID
    type: ShipmentEventType
    source: ShipmentEventSource
    reason: str | None
    occurred_at: datetime


class ExternalEventIngestResponse(BaseModel):
    shipment: ShipmentResponse
    event: ShipmentEventResponse
