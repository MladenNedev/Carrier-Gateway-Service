from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.errors import error_response
from app.domain.errors import DuplicatedError, NotFoundError
from app.persistence.repositories import MerchantRepository
from app.persistence.session import get_db
from app.schemas.merchant import MerchantCreate, MerchantResponse
from app.services.merchant_service import MerchantService

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.post("", response_model=MerchantResponse)
def create_merchant(
    payload: MerchantCreate,
    db: Session = Depends(get_db),
):
    repo = MerchantRepository(db)
    service = MerchantService(repo)

    try:
        merchant = service.create_merchant(payload.name)
    except DuplicatedError as e:
        return error_response(409, "duplicate", str(e))

    return merchant


@router.get("", response_model=list[MerchantResponse])
def list_merchants(db: Session = Depends(get_db)):
    service = MerchantService(MerchantRepository(db))
    return service.list_merchants()


@router.get("/{merchant_id}", response_model=MerchantResponse)
def get_merchant(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    service = MerchantService(MerchantRepository(db))
    try:
        return service.get_merchant(merchant_id)
    except NotFoundError as e:
        return error_response(404, "not_found", str(e))
