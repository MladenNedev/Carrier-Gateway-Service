from sqlalchemy.orm import Session
from .models import MerchantModel

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