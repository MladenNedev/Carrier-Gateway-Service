from sqlalchemy.orm import Session
from .models import MerchantModel, ShipmentEventModel, ShipmentModel
from uuid import UUID

class ShipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, shipment_id: UUID) -> ShipmentModel | None:
        return (
            self.db
            .query(ShipmentModel)
            .filter(ShipmentModel.id == shipment_id)
            .first()
        )

    def get_by_merchant_id_and_external_reference(self, merchant_id: UUID, external_reference: str) -> ShipmentModel | None:
        return (
            self.db
            .query(ShipmentModel)
            .filter(
                ShipmentModel.merchant_id == merchant_id,
                ShipmentModel.external_reference == external_reference,
            )
            .first()
        )

    def list(self) -> list[ShipmentModel]:
        return (
            self.db
            .query(ShipmentModel)
            .all()
        )

    def create(self, shipment: ShipmentModel) -> ShipmentModel:
        self.db.add(shipment)
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

class ShipmentEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, shipment_event_id: UUID) -> ShipmentEventModel | None:
        return (
            self.db
            .query(ShipmentEventModel)
            .filter(ShipmentEventModel.id == shipment_event_id)
            .first() 
        )

    def create(self, shipment_event: ShipmentEventModel) -> ShipmentEventModel:
        self.db.add(shipment_event)
        self.db.commit()
        self.db.refresh(shipment_event)
        return shipment_event


class MerchantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> MerchantModel | None:
        return self.db.query(MerchantModel).filter_by(name=name).first()

    def save(self, merchant: MerchantModel) -> MerchantModel:
        self.db.add(merchant)
        self.db.commit()
        self.db.refresh(merchant)
        return merchant

    def get_by_id(self, merchant_id: UUID):
        return (
            self.db
            .query(MerchantModel)
            .filter(MerchantModel.id == merchant_id)
            .first()
        )

    def list(self):
        return self.db.query(MerchantModel).all()