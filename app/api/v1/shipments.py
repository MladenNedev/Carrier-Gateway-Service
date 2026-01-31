from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.errors import error_response
from app.domain.errors import NotFoundError
from app.domain.shipment import ShipmentStatus
from app.persistence.repositories import (
    MerchantRepository,
    ShipmentEventRepository,
    ShipmentRepository,
)
from app.persistence.session import get_db
from app.schemas.shipment_events import ShipmentEventCreate, ShipmentEventResponse
from app.schemas.shipments import ShipmentCreate, ShipmentResponse, ShipmentStatusUpdate
from app.services.results import ShipmentCreateResponse
from app.services.shipment_service import ShipmentService

router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.post("", response_model=ShipmentResponse)
def create_shipment(
    payload: ShipmentCreate,
    db: Session = Depends(get_db),
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
        return error_response(404, "not_found", str(e))


@router.get("", response_model=list[ShipmentResponse])
def list_shipments(
    merchant_id: UUID | None = None,
    status: ShipmentStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
    )
    return service.list_shipments(
        merchant_id=merchant_id,
        status=status,
        limit=limit,
        offset=offset,
    )


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
        return error_response(404, "not_found", str(e))


@router.post("/{shipment_id}/status", response_model=ShipmentResponse)
def update_shipment_status(
    shipment_id: UUID,
    payload: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
    )
    try:
        return service.update_status(shipment_id, payload.status)
    except NotFoundError as e:
        return error_response(404, "not_found", str(e))
    except ValueError as e:
        return error_response(400, "invalid_transition", str(e))


@router.post("/{shipment_id}/events", response_model=ShipmentEventResponse)
def add_shipment_event(
    shipment_id: UUID,
    payload: ShipmentEventCreate,
    db: Session = Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
        ShipmentEventRepository(db),
    )
    try:
        return service.add_event(shipment_id, payload)
    except NotFoundError as e:
        return error_response(404, "not_found", str(e))


@router.get("/{shipment_id}/events", response_model=list[ShipmentEventResponse])
def list_shipment_events(
    shipment_id: UUID,
    db: Session = Depends(get_db),
):
    service = ShipmentService(
        ShipmentRepository(db),
        MerchantRepository(db),
        ShipmentEventRepository(db),
    )
    try:
        return service.list_events(shipment_id)
    except NotFoundError as e:
        return error_response(404, "not_found", str(e))
