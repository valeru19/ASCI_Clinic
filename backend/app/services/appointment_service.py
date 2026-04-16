import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.repositories.appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from app.schemas.appointments import (
    AppointmentCancelRequest,
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)
from app.schemas.auth import CurrentUserResponse


def _to_response(
    item: Appointment,
    *,
    patient_full_name: str | None = None,
    doctor_full_name: str | None = None,
) -> AppointmentResponse:
    return AppointmentResponse(
        id=str(item.id),
        patient_id=str(item.patient_id),
        patient_full_name=patient_full_name,
        doctor_id=str(item.doctor_id),
        doctor_full_name=doctor_full_name,
        slot_id=str(item.slot_id),
        status=item.status,
        created_at=item.created_at,
    )


class AppointmentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SQLAlchemyAppointmentRepository(session)

    def create(
        self,
        payload: AppointmentCreateRequest,
        current_user: CurrentUserResponse,
    ) -> AppointmentResponse:
        if not self.repo.patient_exists(payload.patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )
        if not self.repo.doctor_exists(payload.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )
        slot = self.repo.get_slot(payload.slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found",
            )
        if slot.status != "available":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is not available",
            )
        if self.repo.is_slot_already_booked(payload.slot_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is already booked",
            )

        schedule = self.repo.get_schedule_for_slot(slot)
        if not schedule or str(schedule.doctor_id) != payload.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot does not belong to selected doctor",
            )

        appointment = Appointment(
            slot_id=uuid.UUID(payload.slot_id),
            patient_id=uuid.UUID(payload.patient_id),
            doctor_id=uuid.UUID(payload.doctor_id),
            status="planned",
            reason=payload.reason.strip() if payload.reason else None,
        )
        created = self.repo.create(appointment)
        slot.status = "booked"
        self.session.add(slot)
        self.session.commit()
        return _to_response(
            created,
            patient_full_name=self.repo.get_patient_full_name(str(created.patient_id)),
            doctor_full_name=self.repo.get_doctor_full_name(str(created.doctor_id)),
        )

    def list_appointments(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        status_value: str | None,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> AppointmentListResponse:
        total = self.repo.count_filtered(
            doctor_id=doctor_id,
            patient_id=patient_id,
            status=status_value,
        )
        rows = self.repo.list_filtered(
            doctor_id=doctor_id,
            patient_id=patient_id,
            status=status_value,
            skip=skip,
            limit=limit,
        )
        return AppointmentListResponse(
            items=[
                _to_response(
                    x,
                    patient_full_name=self.repo.get_patient_full_name(str(x.patient_id)),
                    doctor_full_name=self.repo.get_doctor_full_name(str(x.doctor_id)),
                )
                for x in rows
            ],
            total=total,
        )

    def cancel(
        self,
        appointment_id: str,
        payload: AppointmentCancelRequest,
        current_user: CurrentUserResponse,
    ) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )
        if appt.status in {"cancelled", "completed", "no_show"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Appointment cannot be cancelled in current status",
            )

        slot = self.repo.get_slot(str(appt.slot_id))
        appt.status = "cancelled"
        if payload.reason:
            appt.reason = payload.reason.strip()
        appt.updated_at = datetime.now(UTC)
        if slot:
            slot.status = "available"
            self.session.add(slot)
        self.session.add(appt)
        self.session.commit()
        self.session.refresh(appt)
        return _to_response(
            appt,
            patient_full_name=self.repo.get_patient_full_name(str(appt.patient_id)),
            doctor_full_name=self.repo.get_doctor_full_name(str(appt.doctor_id)),
        )

    def reschedule(
        self,
        appointment_id: str,
        payload: AppointmentRescheduleRequest,
        current_user: CurrentUserResponse,
    ) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )
        if appt.status in {"cancelled", "completed", "no_show"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Appointment cannot be rescheduled in current status",
            )

        new_slot = self.repo.get_slot(payload.slot_id)
        if not new_slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New slot not found",
            )
        if new_slot.status != "available":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New slot is not available",
            )
        if self.repo.is_slot_already_booked(payload.slot_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New slot is already booked",
            )

        new_schedule = self.repo.get_schedule_for_slot(new_slot)
        if not new_schedule or str(new_schedule.doctor_id) != str(appt.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New slot must belong to same doctor",
            )

        old_slot = self.repo.get_slot(str(appt.slot_id))
        if old_slot:
            old_slot.status = "available"
            self.session.add(old_slot)

        new_slot.status = "booked"
        appt.slot_id = uuid.UUID(payload.slot_id)
        appt.updated_at = datetime.now(UTC)

        self.session.add(new_slot)
        self.session.add(appt)
        self.session.commit()
        self.session.refresh(appt)
        return _to_response(
            appt,
            patient_full_name=self.repo.get_patient_full_name(str(appt.patient_id)),
            doctor_full_name=self.repo.get_doctor_full_name(str(appt.doctor_id)),
        )

