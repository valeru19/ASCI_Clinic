from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.models.schedule import Schedule, ScheduleException, ScheduleSlot
from app.infrastructure.repositories.schedule_repository import SQLAlchemyScheduleRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.schedules import (
    ScheduleCreateRequest,
    ScheduleExceptionCreateRequest,
    ScheduleExceptionResponse,
    ScheduleListResponse,
    ScheduleResponse,
    ScheduleSlotGenerateRequest,
    ScheduleSlotGenerateResponse,
    ScheduleSlotListResponse,
    ScheduleSlotResponse,
)


def _schedule_to_response(item: Schedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=str(item.id),
        doctor_id=str(item.doctor_id),
        weekday=item.weekday,
        start_time=item.start_time,
        end_time=item.end_time,
        slot_minutes=item.slot_minutes,
        is_active=item.is_active,
    )


def _slot_to_response(item: ScheduleSlot) -> ScheduleSlotResponse:
    return ScheduleSlotResponse(
        id=str(item.id),
        schedule_id=str(item.schedule_id),
        start_at=item.start_at,
        end_at=item.end_at,
        status=item.status,
    )


def _exception_to_response(item: ScheduleException) -> ScheduleExceptionResponse:
    return ScheduleExceptionResponse(
        id=str(item.id),
        doctor_id=str(item.doctor_id),
        date_from=item.date_from,
        date_to=item.date_to,
        reason=item.reason,
    )


class ScheduleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SQLAlchemyScheduleRepository(session)

    def create_schedule(
        self,
        payload: ScheduleCreateRequest,
        current_user: CurrentUserResponse,
    ) -> ScheduleResponse:
        if payload.slot_minutes not in (15, 30, 60):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="slot_minutes must be 15, 30 or 60",
            )
        if payload.end_time <= payload.start_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="end_time must be greater than start_time",
            )
        if not self.repo.doctor_exists(payload.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )
        if self.repo.has_overlap(
            doctor_id=payload.doctor_id,
            weekday=payload.weekday,
            start_time=payload.start_time,
            end_time=payload.end_time,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Schedule overlaps existing interval",
            )

        schedule = Schedule(
            doctor_id=payload.doctor_id,
            weekday=payload.weekday,
            start_time=payload.start_time,
            end_time=payload.end_time,
            slot_minutes=payload.slot_minutes,
            is_active=payload.is_active,
        )
        created = self.repo.create_schedule(schedule)
        self.session.commit()
        return _schedule_to_response(created)

    def list_schedules(
        self,
        *,
        doctor_id: str | None,
        weekday: int | None,
        include_inactive: bool,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> ScheduleListResponse:
        if include_inactive and current_user.role not in {"admin", "registrar"}:
            include_inactive = False

        total = self.repo.count_schedules(
            doctor_id=doctor_id,
            weekday=weekday,
            include_inactive=include_inactive,
        )
        rows = self.repo.list_schedules(
            doctor_id=doctor_id,
            weekday=weekday,
            include_inactive=include_inactive,
            skip=skip,
            limit=limit,
        )
        return ScheduleListResponse(
            items=[_schedule_to_response(row) for row in rows],
            total=total,
        )

    def generate_slots(
        self,
        payload: ScheduleSlotGenerateRequest,
        current_user: CurrentUserResponse,
    ) -> ScheduleSlotGenerateResponse:
        schedule = self.repo.get_schedule(payload.schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        if payload.date_to < payload.date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="date_to must be greater than or equal to date_from",
            )

        slots = self.repo.generate_slots(
            schedule=schedule,
            date_from=payload.date_from,
            date_to=payload.date_to,
        )
        self.session.commit()
        return ScheduleSlotGenerateResponse(
            created=len(slots),
            slots=[_slot_to_response(slot) for slot in slots],
        )

    def create_exception(
        self,
        payload: ScheduleExceptionCreateRequest,
        current_user: CurrentUserResponse,
    ) -> ScheduleExceptionResponse:
        if payload.date_to < payload.date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="date_to must be greater than or equal to date_from",
            )
        if not self.repo.doctor_exists(payload.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )

        item = ScheduleException(
            doctor_id=payload.doctor_id,
            date_from=payload.date_from,
            date_to=payload.date_to,
            reason=payload.reason.strip(),
        )
        created = self.repo.create_exception(item)
        self.session.commit()
        return _exception_to_response(created)

    def list_slots(
        self,
        *,
        doctor_id: str | None,
        date_from: date,
        date_to: date,
        status_value: str | None,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> ScheduleSlotListResponse:
        if date_to < date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="date_to must be greater than or equal to date_from",
            )

        total = self.repo.count_slots(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
            status=status_value,
        )
        rows = self.repo.list_slots(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
            status=status_value,
            skip=skip,
            limit=limit,
        )
        return ScheduleSlotListResponse(
            items=[_slot_to_response(row) for row in rows],
            total=total,
        )

