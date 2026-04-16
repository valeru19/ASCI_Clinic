from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.models.patient import Patient
from app.infrastructure.repositories.patient_repository import SQLAlchemyPatientRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.patients import (
    PatientCreateRequest,
    PatientListResponse,
    PatientResponse,
    PatientUpdateRequest,
)


def _to_response(p: Patient) -> PatientResponse:
    return PatientResponse(
        id=str(p.id),
        last_name=p.last_name,
        first_name=p.first_name,
        middle_name=p.middle_name,
        birth_date=p.birth_date,
        gender=p.gender,
        phone=p.phone,
        email=p.email,
        insurance_number=p.insurance_number,
        address=p.address,
        is_active=p.is_active,
    )


class PatientService:
    def __init__(self, session: Session) -> None:
        self.repo = SQLAlchemyPatientRepository(session)
        self.session = session

    def create(
        self,
        payload: PatientCreateRequest,
        current_user: CurrentUserResponse,
    ) -> PatientResponse:
        patient = Patient(
            last_name=payload.last_name.strip(),
            first_name=payload.first_name.strip(),
            middle_name=payload.middle_name.strip() if payload.middle_name else None,
            birth_date=payload.birth_date,
            gender=payload.gender,
            phone=payload.phone,
            email=str(payload.email) if payload.email else None,
            insurance_number=payload.insurance_number,
            address=payload.address,
            is_active=True,
        )
        created = self.repo.create(patient)
        self.session.commit()
        return _to_response(created)

    def list_patients(
        self,
        *,
        q: Optional[str],
        birth_date: Optional[date],
        include_inactive: bool,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> PatientListResponse:
        if include_inactive and current_user.role not in {"admin", "registrar"}:
            include_inactive = False

        total = self.repo.count_filtered(
            q=q,
            birth_date=birth_date,
            include_inactive=include_inactive,
        )
        rows = self.repo.list_filtered(
            q=q,
            birth_date=birth_date,
            include_inactive=include_inactive,
            skip=skip,
            limit=limit,
        )
        return PatientListResponse(
            items=[_to_response(p) for p in rows],
            total=total,
        )

    def get_patient(
        self,
        patient_id: str,
        current_user: CurrentUserResponse,
    ) -> PatientResponse:
        patient = self.repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        return _to_response(patient)

    def update_patient(
        self,
        patient_id: str,
        payload: PatientUpdateRequest,
        current_user: CurrentUserResponse,
    ) -> PatientResponse:
        patient = self.repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        data = payload.model_dump(exclude_unset=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No fields to update",
            )
        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])
        for key, value in data.items():
            if isinstance(value, str):
                value = value.strip()
                if key == "middle_name" and value == "":
                    value = None
            setattr(patient, key, value)

        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return _to_response(patient)

    def soft_delete(
        self,
        patient_id: str,
        current_user: CurrentUserResponse,
    ) -> PatientResponse:
        patient = self.repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        patient.is_active = False
        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return _to_response(patient)
