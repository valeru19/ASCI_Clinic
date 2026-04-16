import uuid
from datetime import date
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.patient import Patient


class SQLAlchemyPatientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, patient: Patient) -> Patient:
        self.session.add(patient)
        self.session.flush()
        self.session.refresh(patient)
        return patient

    def get_by_id(self, patient_id: str) -> Optional[Patient]:
        try:
            pid = uuid.UUID(patient_id)
        except ValueError:
            return None
        stmt = select(Patient).where(Patient.id == pid)
        return self.session.execute(stmt).scalar_one_or_none()

    def count_filtered(
        self,
        *,
        q: Optional[str],
        birth_date: Optional[date],
        include_inactive: bool,
    ) -> int:
        stmt = select(func.count(Patient.id)).select_from(Patient)
        if not include_inactive:
            stmt = stmt.where(Patient.is_active.is_(True))
        if birth_date is not None:
            stmt = stmt.where(Patient.birth_date == birth_date)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Patient.last_name.ilike(pattern),
                    Patient.first_name.ilike(pattern),
                    Patient.middle_name.ilike(pattern),
                )
            )
        return int(self.session.execute(stmt).scalar_one())

    def list_filtered(
        self,
        *,
        q: Optional[str],
        birth_date: Optional[date],
        include_inactive: bool,
        skip: int,
        limit: int,
    ) -> list[Patient]:
        stmt = select(Patient)
        if not include_inactive:
            stmt = stmt.where(Patient.is_active.is_(True))
        if birth_date is not None:
            stmt = stmt.where(Patient.birth_date == birth_date)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Patient.last_name.ilike(pattern),
                    Patient.first_name.ilike(pattern),
                    Patient.middle_name.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Patient.last_name, Patient.first_name, Patient.id)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
