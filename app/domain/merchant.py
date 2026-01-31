from dataclasses import dataclass
from uuid import UUID


@dataclass
class Merchant:
    id: UUID
    name: str
