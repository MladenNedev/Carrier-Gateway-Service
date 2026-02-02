from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.shipment import ShipmentStatus


class ShipmentCreate(BaseModel):
    merchant_id: UUID
    name: str
    external_reference: str


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    merchant_id: UUID
    name: str
    status: str
    external_reference: str


class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatus
