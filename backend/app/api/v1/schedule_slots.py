from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_schedule_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.schedules import (
    ScheduleSlotGenerateRequest,
    ScheduleSlotGenerateResponse,
    ScheduleSlotListResponse,
)
from app.services.schedule_service import ScheduleService

router = APIRouter()


@router.post(
    "/generate",
    response_model=ScheduleSlotGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_slots(
    payload: ScheduleSlotGenerateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleSlotGenerateResponse:
    return service.generate_slots(payload, current_user)


@router.get("/", response_model=ScheduleSlotListResponse)
def list_slots(
    doctor_id: str | None = Query(default=None),
    date_from: date = Query(...),
    date_to: date = Query(...),
    status_value: str | None = Query(
        default="available",
        alias="status",
        pattern="^(available|booked|blocked|cancelled)$",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleSlotListResponse:
    return service.list_slots(
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
        status_value=status_value,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )
