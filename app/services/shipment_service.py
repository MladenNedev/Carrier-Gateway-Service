from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.adapters.base import AdapterResult
from app.domain.errors import NotFoundError
from app.domain.shipment import Shipment, ShipmentStatus, can_transition
from app.domain.shipment_event import ShipmentEventSource, ShipmentTrackingEvent
from app.persistence.models import ShipmentEventModel, ShipmentModel
from app.persistence.repositories import (
    MerchantRepository,
    ShipmentEventRepository,
    ShipmentRepository,
)
from app.schemas.shipment_events import ShipmentEventCreate
from app.schemas.shipments import ShipmentCreate
from app.services.results import ShipmentCreateResponse


class ShipmentService:
    def __init__(
        self,
        shipment_repo: ShipmentRepository,
        merchant_repo: MerchantRepository,
        event_repo: ShipmentEventRepository | None = None,
    ):
        self.shipment_repo = shipment_repo
        self.merchant_repo = merchant_repo
        self.event_repo = event_repo

    def create_shipment(self, data: ShipmentCreate) -> ShipmentCreateResponse:
        merchant = self.merchant_repo.get_by_id(data.merchant_id)
        if not merchant:
            raise NotFoundError(f"Merchant {data.merchant_id} not found")

        existing = self.shipment_repo.get_by_merchant_id_and_external_reference(
            data.merchant_id,
            data.external_reference,
        )
        if existing:
            shipment = Shipment(
                id=existing.id,
                merchant_id=existing.merchant_id,
                name=existing.name,
                external_reference=existing.external_reference,
                status=ShipmentStatus(existing.status),
            )
            return ShipmentCreateResponse(shipment=shipment, created=False)

        model = ShipmentModel(
            merchant_id=data.merchant_id,
            name=data.name,
            external_reference=data.external_reference,
            status=ShipmentStatus.CREATED,
        )
        try:
            saved = self.shipment_repo.create(model)
        except IntegrityError as exc:
            self.shipment_repo.db.rollback()
            existing = self.shipment_repo.get_by_merchant_id_and_external_reference(
                data.merchant_id,
                data.external_reference,
            )
            if existing:
                shipment = Shipment(
                    id=existing.id,
                    merchant_id=existing.merchant_id,
                    name=existing.name,
                    external_reference=existing.external_reference,
                    status=ShipmentStatus(existing.status),
                )
                return ShipmentCreateResponse(shipment=shipment, created=False)
            raise exc

        shipment = Shipment(
            id=saved.id,
            merchant_id=saved.merchant_id,
            name=saved.name,
            external_reference=saved.external_reference,
            status=ShipmentStatus(saved.status),
        )
        return ShipmentCreateResponse(shipment=shipment, created=True)

    def get_shipment(self, shipment_id: UUID) -> Shipment:

        model = self.shipment_repo.get_by_id(shipment_id)
        if not model:
            raise NotFoundError(f"Shipment {shipment_id} not found")
        return Shipment(
            id=model.id,
            merchant_id=model.merchant_id,
            name=model.name,
            external_reference=model.external_reference,
            status=ShipmentStatus(model.status),
        )

    def list_shipments(
        self,
        merchant_id: UUID | None = None,
        status: ShipmentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Shipment]:
        models = self.shipment_repo.list_filtered(
            merchant_id=merchant_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        return [
            Shipment(
                id=m.id,
                merchant_id=m.merchant_id,
                name=m.name,
                external_reference=m.external_reference,
                status=ShipmentStatus(m.status),
            )
            for m in models
        ]

    def update_status(self, shipment_id: UUID, new_status: ShipmentStatus) -> Shipment:
        model = self.shipment_repo.get_by_id(shipment_id)
        if not model:
            raise NotFoundError(f"Shipment {shipment_id} not found")

        current_status = ShipmentStatus(model.status)
        if not can_transition(current_status, new_status):
            raise ValueError(f"Invalid transition from {current_status} to {new_status}")

        model.status = new_status
        saved = self.shipment_repo.update_status(model)
        return Shipment(
            id=saved.id,
            merchant_id=saved.merchant_id,
            name=saved.name,
            external_reference=saved.external_reference,
            status=ShipmentStatus(saved.status),
        )

    def add_event(self, shipment_id: UUID, payload: ShipmentEventCreate) -> ShipmentTrackingEvent:
        if not self.event_repo:
            raise RuntimeError("Shipment event repository is not configured")

        model = self.shipment_repo.get_by_id(shipment_id)
        if not model:
            raise NotFoundError(f"Shipment {shipment_id} not found")

        event_kwargs = {
            "shipment_id": shipment_id,
            "type": payload.type,
            "source": payload.source,
            "reason": payload.reason,
        }
        if payload.occurred_at is not None:
            event_kwargs["occurred_at"] = payload.occurred_at

        event = ShipmentEventModel(**event_kwargs)
        saved = self.event_repo.create(event)
        return ShipmentTrackingEvent(
            id=saved.id,
            shipment_id=saved.shipment_id,
            type=saved.type,
            source=saved.source,
            reason=saved.reason,
            occurred_at=saved.occurred_at,
        )

    def list_events(self, shipment_id: UUID) -> list[ShipmentTrackingEvent]:
        if not self.event_repo:
            raise RuntimeError("Shipment event repository is not configured")

        model = self.shipment_repo.get_by_id(shipment_id)
        if not model:
            raise NotFoundError(f"Shipment {shipment_id} not found")

        events = self.event_repo.list_by_shipment_id(shipment_id)
        return [
            ShipmentTrackingEvent(
                id=e.id,
                shipment_id=e.shipment_id,
                type=e.type,
                source=e.source,
                reason=e.reason,
                occurred_at=e.occurred_at,
            )
            for e in events
        ]

    def process_external_event(
        self,
        adapter_result: AdapterResult,
    ) -> tuple[Shipment, ShipmentTrackingEvent]:
        if not self.event_repo:
            raise RuntimeError("Shipment event repository is not configured")

        shipment = self.shipment_repo.get_by_merchant_id_and_external_reference(
            adapter_result.merchant_id,
            adapter_result.shipment_external_reference,
        )
        if not shipment:
            raise NotFoundError(
                f"Shipment {adapter_result.shipment_external_reference} not found for merchant {adapter_result.merchant_id}"
            )

        if adapter_result.shipment_status is not None:
            current_status = ShipmentStatus(shipment.status)
            if not can_transition(current_status, adapter_result.shipment_status):
                raise ValueError(
                    f"Invalid transition from {current_status} to {adapter_result.shipment_status}"
                )
            shipment.status = adapter_result.shipment_status
            shipment = self.shipment_repo.update_status(shipment)

        event = ShipmentEventModel(
            shipment_id=shipment.id,
            type=adapter_result.event_type,
            source=ShipmentEventSource.SYSTEM,
            reason=adapter_result.reason,
            occurred_at=adapter_result.occurred_at,
        )
        saved_event = self.event_repo.create(event)

        updated_shipment = Shipment(
            id=shipment.id,
            merchant_id=shipment.merchant_id,
            name=shipment.name,
            external_reference=shipment.external_reference,
            status=ShipmentStatus(shipment.status),
        )
        tracking_event = ShipmentTrackingEvent(
            id=saved_event.id,
            shipment_id=saved_event.shipment_id,
            type=saved_event.type,
            source=saved_event.source,
            reason=saved_event.reason,
            occurred_at=saved_event.occurred_at,
        )
        return updated_shipment, tracking_event
