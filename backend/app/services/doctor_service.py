from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.infrastructure.repositories.doctor_repository import SQLAlchemyDoctorRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.doctors import (
    DoctorCreateRequest,
    DoctorEmploymentUpdateRequest,
    DoctorListItem,
    DoctorListResponse,
)


class DoctorService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SQLAlchemyDoctorRepository(session)

    def list_doctors(
        self,
        *,
        include_inactive: bool,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> DoctorListResponse:
        if include_inactive and current_user.role != "admin":
            include_inactive = False

        total = self.repo.count_doctors(include_inactive=include_inactive)
        rows = self.repo.list_doctors(
            include_inactive=include_inactive,
            skip=skip,
            limit=limit,
        )
        return DoctorListResponse(
            items=[DoctorListItem(**row) for row in rows],
            total=total,
        )

    def create_doctor(
        self,
        payload: DoctorCreateRequest,
        current_user: CurrentUserResponse,
    ) -> DoctorListItem:
        for specialty_id in payload.specialty_ids:
            if not self.repo.specialty_exists(specialty_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Specialty not found: {specialty_id}",
                )
        try:
            row = self.repo.create_doctor(
                username=payload.username.strip(),
                email=str(payload.email).strip().lower(),
                password_hash=get_password_hash(payload.password),
                last_name=payload.last_name.strip(),
                first_name=payload.first_name.strip(),
                middle_name=payload.middle_name.strip() if payload.middle_name else None,
                license_number=payload.license_number.strip(),
                experience_years=payload.experience_years,
                specialty_ids=payload.specialty_ids,
                monthly_salary=payload.monthly_salary,
                bonus_percent=payload.bonus_percent,
                is_active=payload.is_active,
            )
            self.session.commit()
            return DoctorListItem(**row)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor with same username, email or license already exists",
            ) from exc

    def update_employment(
        self,
        doctor_id: str,
        payload: DoctorEmploymentUpdateRequest,
        current_user: CurrentUserResponse,
    ) -> DoctorListItem:
        if (
            payload.monthly_salary is None
            and payload.bonus_percent is None
            and payload.is_active is None
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No fields to update",
            )
        row = self.repo.update_doctor_employment(
            doctor_id=doctor_id,
            monthly_salary=payload.monthly_salary,
            bonus_percent=payload.bonus_percent,
            is_active=payload.is_active,
        )
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )
        self.session.commit()
        return DoctorListItem(**row)

    def list_specialties(self) -> list[dict]:
        return self.repo.list_specialties()
