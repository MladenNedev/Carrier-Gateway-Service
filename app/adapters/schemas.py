from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ExternalCarrierEvent(BaseModel):
    carrier: str
    merchant_id: UUID
    external_reference: str
    event_code: str
    event_time: datetime
