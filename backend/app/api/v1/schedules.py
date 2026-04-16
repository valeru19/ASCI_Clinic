from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_schedule_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.schedules import (
    ScheduleCreateRequest,
    ScheduleListResponse,
    ScheduleResponse,
)
from app.services.schedule_service import ScheduleService

router = APIRouter()


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleResponse:
    return service.create_schedule(payload, current_user)


@router.get("/", response_model=ScheduleListResponse)
def list_schedules(
    doctor_id: Optional[str] = Query(None),
    weekday: Optional[int] = Query(None, ge=1, le=7),
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleListResponse:
    return service.list_schedules(
        doctor_id=doctor_id,
        weekday=weekday,
        include_inactive=include_inactive,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )
