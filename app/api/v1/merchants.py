from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.merchant import MerchantCreate, MerchantResponse
from app.persistance.session import get_db
from app.persistance.repositories import MerchantRepository
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return merchant