import uuid

from sqlalchemy import and_, func, select, text
from sqlalchemy.orm import Session

from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.schedule import Schedule, ScheduleSlot


class SQLAlchemyAppointmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def patient_exists(self, patient_id: str) -> bool:
        try:
            pid = uuid.UUID(patient_id)
        except ValueError:
            return False
        row = self.session.execute(
            text(
                "SELECT 1 FROM clinic.patients WHERE id = :patient_id AND is_active = true LIMIT 1"
            ),
            {"patient_id": str(pid)},
        ).first()
        return row is not None

    def doctor_exists(self, doctor_id: str) -> bool:
        try:
            did = uuid.UUID(doctor_id)
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.doctors WHERE id = :doctor_id LIMIT 1"),
            {"doctor_id": str(did)},
        ).first()
        return row is not None

    def get_slot(self, slot_id: str) -> ScheduleSlot | None:
        try:
            sid = uuid.UUID(slot_id)
        except ValueError:
            return None
        stmt = select(ScheduleSlot).where(ScheduleSlot.id == sid)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_schedule_for_slot(self, slot: ScheduleSlot) -> Schedule | None:
        stmt = select(Schedule).where(Schedule.id == slot.schedule_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, appointment: Appointment) -> Appointment:
        self.session.add(appointment)
        self.session.flush()
        self.session.refresh(appointment)
        return appointment

    def get_by_id(self, appointment_id: str) -> Appointment | None:
        try:
            aid = uuid.UUID(appointment_id)
        except ValueError:
            return None
        stmt = select(Appointment).where(Appointment.id == aid)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_filtered(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        status: str | None,
        skip: int,
        limit: int,
    ) -> list[Appointment]:
        stmt = select(Appointment)

        if doctor_id:
            try:
                stmt = stmt.where(Appointment.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return []
        if patient_id:
            try:
                stmt = stmt.where(Appointment.patient_id == uuid.UUID(patient_id))
            except ValueError:
                return []
        if status:
            stmt = stmt.where(Appointment.status == status)

        stmt = stmt.order_by(Appointment.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def count_filtered(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        status: str | None,
    ) -> int:
        stmt = select(func.count(Appointment.id)).select_from(Appointment)

        if doctor_id:
            try:
                stmt = stmt.where(Appointment.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return 0
        if patient_id:
            try:
                stmt = stmt.where(Appointment.patient_id == uuid.UUID(patient_id))
            except ValueError:
                return 0
        if status:
            stmt = stmt.where(Appointment.status == status)

        return int(self.session.execute(stmt).scalar_one())

    def is_slot_already_booked(self, slot_id: str) -> bool:
        try:
            sid = uuid.UUID(slot_id)
        except ValueError:
            return True
        stmt = select(func.count(Appointment.id)).where(Appointment.slot_id == sid)
        return int(self.session.execute(stmt).scalar_one()) > 0

    def get_patient_full_name(self, patient_id: str) -> str | None:
        try:
            pid = str(uuid.UUID(patient_id))
        except ValueError:
            return None
        row = self.session.execute(
            text(
                """
                SELECT TRIM(last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '')) AS full_name
                FROM clinic.patients
                WHERE id = CAST(:patient_id AS uuid)
                """
            ),
            {"patient_id": pid},
        ).mappings().first()
        if not row or not row["full_name"]:
            return None
        return str(row["full_name"])

    def get_doctor_full_name(self, doctor_id: str) -> str | None:
        try:
            did = str(uuid.UUID(doctor_id))
        except ValueError:
            return None
        row = self.session.execute(
            text(
                """
                SELECT
                    COALESCE(
                        NULLIF(TRIM(
                            COALESCE(d.last_name, '') || ' ' ||
                            COALESCE(d.first_name, '') || ' ' ||
                            COALESCE(d.middle_name, '')
                        ), ''),
                        u.username
                    ) AS full_name
                FROM clinic.doctors d
                LEFT JOIN clinic.users u ON u.id = d.user_id
                WHERE d.id = CAST(:doctor_id AS uuid)
                """
            ),
            {"doctor_id": did},
        ).mappings().first()
        if not row or not row["full_name"]:
            return None
        return str(row["full_name"])

    def doctor_has_appointment_in_slot(self, doctor_id: str, slot_id: str) -> bool:
        try:
            did = uuid.UUID(doctor_id)
            sid = uuid.UUID(slot_id)
        except ValueError:
            return False
        stmt = select(func.count(Appointment.id)).where(
            and_(
                Appointment.doctor_id == did,
                Appointment.slot_id == sid,
            )
        )
        return int(self.session.execute(stmt).scalar_one()) > 0
