import uuid

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.diagnosis import Diagnosis
from app.infrastructure.db.models.prescription import Prescription
from app.infrastructure.db.models.referral import Referral
from app.infrastructure.db.models.visit import Visit


class SQLAlchemyVisitRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_appointment(self, appointment_id: str) -> Appointment | None:
        try:
            aid = uuid.UUID(appointment_id)
        except ValueError:
            return None
        stmt = select(Appointment).where(Appointment.id == aid)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_doctor_id_by_user_id(self, user_id: str) -> str | None:
        row = self.session.execute(
            text(
                """
                SELECT d.id::text AS id
                FROM clinic.doctors d
                WHERE d.user_id = CAST(:user_id AS uuid)
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).mappings().first()
        if not row:
            return None
        return str(row["id"])

    def get_patient_full_name(self, patient_id: str) -> str:
        try:
            pid = str(uuid.UUID(patient_id))
        except ValueError:
            return "Неизвестный пациент"
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
            return "Неизвестный пациент"
        return str(row["full_name"])

    def get_doctor_full_name(self, doctor_id: str) -> str:
        try:
            did = str(uuid.UUID(doctor_id))
        except ValueError:
            return "Неизвестный врач"
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
                        u.username,
                        'Неизвестный врач'
                    ) AS full_name
                FROM clinic.doctors d
                LEFT JOIN clinic.users u ON u.id = d.user_id
                WHERE d.id = CAST(:doctor_id AS uuid)
                """
            ),
            {"doctor_id": did},
        ).mappings().first()
        if not row or not row["full_name"]:
            return "Неизвестный врач"
        return str(row["full_name"])

    def get_by_id(self, visit_id: str) -> Visit | None:
        try:
            vid = uuid.UUID(visit_id)
        except ValueError:
            return None
        stmt = select(Visit).where(Visit.id == vid)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_appointment_id(self, appointment_id: str) -> Visit | None:
        try:
            aid = uuid.UUID(appointment_id)
        except ValueError:
            return None
        stmt = select(Visit).where(Visit.appointment_id == aid)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, visit: Visit) -> Visit:
        self.session.add(visit)
        self.session.flush()
        self.session.refresh(visit)
        return visit

    def list_filtered(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        visit_status: str | None,
        skip: int,
        limit: int,
    ) -> list[tuple[Visit, str, str]]:
        stmt = (
            select(Visit, Appointment.patient_id, Appointment.doctor_id)
            .join(Appointment, Appointment.id == Visit.appointment_id)
            .order_by(Visit.id.desc())
        )

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
        if visit_status:
            stmt = stmt.where(Visit.visit_status == visit_status)

        rows = self.session.execute(stmt.offset(skip).limit(limit)).all()
        return [(row[0], str(row[1]), str(row[2])) for row in rows]

    def count_filtered(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        visit_status: str | None,
    ) -> int:
        stmt = (
            select(func.count(Visit.id))
            .select_from(Visit)
            .join(Appointment, Appointment.id == Visit.appointment_id)
        )

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
        if visit_status:
            stmt = stmt.where(Visit.visit_status == visit_status)

        return int(self.session.execute(stmt).scalar_one())

    def icd10_code_exists(self, code: str) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM clinic.icd10_codes WHERE code = :code LIMIT 1"),
            {"code": code},
        ).first()
        return row is not None

    def count_primary_diagnoses(self, visit_id: str) -> int:
        try:
            vid = uuid.UUID(visit_id)
        except ValueError:
            return 0
        stmt = select(func.count(Diagnosis.id)).where(
            Diagnosis.visit_id == vid,
            Diagnosis.is_primary.is_(True),
        )
        return int(self.session.execute(stmt).scalar_one())

    def create_diagnoses(self, items: list[Diagnosis]) -> list[Diagnosis]:
        self.session.add_all(items)
        self.session.flush()
        for item in items:
            self.session.refresh(item)
        return items

    def medication_exists(self, medication_id: str) -> bool:
        try:
            mid = str(uuid.UUID(medication_id))
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.medications WHERE id = :mid LIMIT 1"),
            {"mid": mid},
        ).first()
        return row is not None

    def create_prescriptions(self, items: list[Prescription]) -> list[Prescription]:
        self.session.add_all(items)
        self.session.flush()
        for item in items:
            self.session.refresh(item)
        return items

    def specialty_exists(self, specialty_id: int) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM clinic.specialties WHERE id = :specialty_id LIMIT 1"),
            {"specialty_id": specialty_id},
        ).first()
        return row is not None

    def doctor_exists(self, doctor_id: str) -> bool:
        try:
            did = str(uuid.UUID(doctor_id))
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.doctors WHERE id = :doctor_id LIMIT 1"),
            {"doctor_id": did},
        ).first()
        return row is not None

    def create_referrals(self, items: list[Referral]) -> list[Referral]:
        self.session.add_all(items)
        self.session.flush()
        for item in items:
            self.session.refresh(item)
        return items
