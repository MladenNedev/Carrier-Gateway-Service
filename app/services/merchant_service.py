from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.domain.errors import DuplicatedError, NotFoundError
from app.domain.merchant import Merchant
from app.persistence.models import MerchantModel
from app.persistence.repositories import MerchantRepository


class MerchantService:
    def __init__(self, repo: MerchantRepository):
        self.repo = repo

    def create_merchant(self, name: str) -> Merchant:
        if self.repo.get_by_name(name=name):
            raise DuplicatedError(f"Merchant {name} already exists")

        try:
            saved = self.repo.save(MerchantModel(name=name))
        except IntegrityError as exc:
            self.repo.db.rollback()
            if self.repo.get_by_name(name=name):
                raise DuplicatedError(f"Merchant {name} already exists") from exc
            raise
        return Merchant(id=saved.id, name=saved.name)

    def get_merchant(self, merchant_id: UUID) -> Merchant:
        model = self.repo.get_by_id(merchant_id)
        if not model:
            raise NotFoundError(f"Merchant {merchant_id} not found")
        return Merchant(id=model.id, name=model.name)

    def list_merchants(self) -> list[Merchant]:
        return [Merchant(id=m.id, name=m.name) for m in self.repo.list()]
