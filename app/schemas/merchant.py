from pydantic import BaseModel
from uuid import UUID

class MerchantCreate(BaseModel):
    name: str

class MerchantResponse(BaseModel):
    id: UUID
    name: str