from pydantic import BaseModel
from uuid import UUID

class ShipmentCreate(BaseModel):
    merchant_id: UUID
    name: str
    external_reference: str | None

class ShipmentResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    name: str
    status: str
    external_reference: str | None

    class Config:
        from_attributes = True