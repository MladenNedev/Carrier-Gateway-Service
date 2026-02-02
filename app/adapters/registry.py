from app.adapters.base import CarrierAdapter
from app.adapters.carrier_stub import MockCarrierAdapter

_REGISTRY: dict[str, CarrierAdapter] = {
    "mock": MockCarrierAdapter(),
}


def get_adapter(carrier: str) -> CarrierAdapter:
    adapter = _REGISTRY.get(carrier)
    if not adapter:
        raise ValueError(f"Unsupported carrier: {carrier}")
    return adapter
