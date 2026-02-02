from uuid import UUID

from pydantic import BaseModel


class MerchantCreate(BaseModel):
    name: str


class MerchantResponse(BaseModel):
    id: UUID
    name: str
