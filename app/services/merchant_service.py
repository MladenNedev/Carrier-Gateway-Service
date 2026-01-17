from app.domain.merchant import Merchant
from app.persistance.repositories import MerchantRepository
from app.persistance.models import MerchantModel

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