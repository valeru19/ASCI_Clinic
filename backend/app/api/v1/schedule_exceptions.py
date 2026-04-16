from fastapi import APIRouter, Depends, status

from app.api.deps import get_schedule_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.schedules import (
    ScheduleExceptionCreateRequest,
    ScheduleExceptionResponse,
)
from app.services.schedule_service import ScheduleService

router = APIRouter()


@router.post(
    "/",
    response_model=ScheduleExceptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exception(
    payload: ScheduleExceptionCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleExceptionResponse:
    return service.create_exception(payload, current_user)
