from datetime import datetime

from pydantic import BaseModel


class ExternalCarrierEvent(BaseModel):
    carrier: str
    external_reference: str
    event_code: str
    event_time: datetime
