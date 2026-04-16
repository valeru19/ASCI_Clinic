from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status

from app.api.deps import get_lab_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.labs import (
    LabOrderCreateRequest,
    LabOrderItemsCreateRequest,
    LabOrderItemsCreateResponse,
    LabOrderResponse,
    LabResultCreateRequest,
    LabResultListResponse,
    LabResultResponse,
)
from app.services.lab_service import LabService

router = APIRouter()


@router.post("/orders", response_model=LabOrderResponse, status_code=status.HTTP_201_CREATED)
def create_lab_order(
    payload: LabOrderCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: LabService = Depends(get_lab_service),
) -> LabOrderResponse:
    return service.create_order(payload, current_user)


@router.post(
    "/orders/{order_id}/items",
    response_model=LabOrderItemsCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_lab_order_items(
    order_id: str,
    payload: LabOrderItemsCreateRequest = Body(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: LabService = Depends(get_lab_service),
) -> LabOrderItemsCreateResponse:
    return service.add_order_items(order_id, payload, current_user)


@router.post("/results", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
def create_lab_result(
    payload: LabResultCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: LabService = Depends(get_lab_service),
) -> LabResultResponse:
    return service.create_result(payload, current_user)


@router.get("/results", response_model=LabResultListResponse)
def list_lab_results(
    patient_id: Optional[str] = Query(None),
    order_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: LabService = Depends(get_lab_service),
) -> LabResultListResponse:
    return service.list_results(
        patient_id=patient_id,
        order_id=order_id,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )
