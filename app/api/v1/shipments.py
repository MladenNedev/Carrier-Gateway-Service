from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.domain.errors import NotFoundError
from app.schemas.shipments import ShipmentCreate, ShipmentResponse
from app.persistence.session import get_db
from app.persistence.repositories import MerchantRepository, ShipmentRepository
from app.services.shipment_service import ShipmentService
from app.services.results import ShipmentCreateResponse

router = APIRouter(prefix="/shipments", tags=["shipments"])

@router.post("", response_model=ShipmentResponse)
def create_shipment(
        payload: ShipmentCreate,
        db: Session =  Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
    )
    try:
        result: ShipmentCreateResponse = service.create_shipment(payload)
        status_code = 201 if result.created else 200
        response_body = ShipmentResponse.model_validate(result.shipment).model_dump(mode="json")
        return JSONResponse(status_code=status_code, content=response_body)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("", response_model=list[ShipmentResponse])
def list_shipments(
        db: Session = Depends(get_db)
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
        )
    return service.list_shipments()

@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(
        shipment_id: UUID,
        db: Session = Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
        )
    try:
        return service.get_shipment(shipment_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
