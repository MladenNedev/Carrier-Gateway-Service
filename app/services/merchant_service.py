from app.domain.merchant import Merchant
from app.persistance.repositories import MerchantRepository
from app.persistance.models import MerchantModel
from app.domain.merchant import Merchant
from uuid import UUID

class MerchantService:
    def __init__(self, repo: MerchantRepository):
        self.repo = repo

    def create_merchant(self, name: str) -> Merchant:
        existing = self.repo.get_by_name(name=name)
        if existing:
            raise ValueError(f"Merchant with name {name} already exists")

        model = MerchantModel(name=name)
        saved = self.repo.save(model)

        return Merchant(
            id=saved.id,
            name=saved.name
        )

    def get_merchant(self, merchant_id: UUID) -> Merchant:
        model = self.repo.get_by_id(merchant_id)
        if not model:
            raise ValueError(f"Merchant with id {merchant_id} does not exist")

        return Merchant(id=model.id, name=model.name)

    def list_merchants(self) -> list[Merchant]:
        return [
            Merchant(id=m.id, name=m.name)
            for m in self.repo.list()
        ]