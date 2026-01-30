from app.domain.errors import NotFoundError
from app.domain.shipment import Shipment, ShipmentStatus
from app.persistence.models import ShipmentModel
from app.persistence.repositories import MerchantRepository, ShipmentRepository
from app.schemas.shipments import ShipmentCreate
from app.services.results import ShipmentCreateResponse

from uuid import UUID


class ShipmentService:
    def __init__(self, shipment_repo: ShipmentRepository, merchant_repo:MerchantRepository):
        self.shipment_repo = shipment_repo
        self.merchant_repo = merchant_repo

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
        saved = self.shipment_repo.create(model)

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
        return Shipment(id=model.id, merchant_id=model.merchant_id, name=model.name, external_reference=model.external_reference, status=ShipmentStatus(model.status))

    def list_shipments(self) -> list[Shipment]:
        model = self.shipment_repo.list()
        return [
            Shipment(id=m.id, merchant_id=m.merchant_id, name=m.name, external_reference=m.external_reference, status=ShipmentStatus(m.status))
            for m in model
        ]
