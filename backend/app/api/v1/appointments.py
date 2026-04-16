from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status

from app.api.deps import get_appointment_service, require_roles
from app.schemas.appointments import (
    AppointmentCancelRequest,
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)
from app.schemas.auth import CurrentUserResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    return service.create(payload, current_user)


@router.get("/", response_model=AppointmentListResponse)
def list_appointments(
    doctor_id: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    status_value: Optional[str] = Query(
        None, alias="status", pattern="^(planned|confirmed|cancelled|completed|no_show)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentListResponse:
    return service.list_appointments(
        doctor_id=doctor_id,
        patient_id=patient_id,
        status_value=status_value,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: str,
    payload: AppointmentCancelRequest | None = Body(default=None),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    return service.cancel(appointment_id, payload or AppointmentCancelRequest(), current_user)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: str,
    payload: AppointmentRescheduleRequest = Body(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    return service.reschedule(appointment_id, payload, current_user)
