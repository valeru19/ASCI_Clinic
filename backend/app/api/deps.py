from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.schemas.auth import CurrentUserResponse
from app.services.auth_service import AuthService
from app.services.appointment_service import AppointmentService
from app.services.doctor_service import DoctorService
from app.services.lab_service import LabService
from app.services.patient_service import PatientService
from app.services.report_service import ReportService
from app.services.schedule_service import ScheduleService
from app.services.visit_service import VisitService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(user_repository=SQLAlchemyUserRepository(session=db))


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is missing",
        )
    return auth_service.get_current_user(subject)


def require_roles(*roles: str):
    allowed_roles = set(roles)

    def role_checker(
        current_user: CurrentUserResponse = Depends(get_current_user),
    ) -> CurrentUserResponse:
        AuthService.ensure_role(current_user, allowed_roles)
        return current_user

    return role_checker


def get_patient_service(db: Session = Depends(get_db)) -> PatientService:
    return PatientService(session=db)


def get_schedule_service(db: Session = Depends(get_db)) -> ScheduleService:
    return ScheduleService(session=db)


def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return AppointmentService(session=db)


def get_visit_service(db: Session = Depends(get_db)) -> VisitService:
    return VisitService(session=db)


def get_lab_service(db: Session = Depends(get_db)) -> LabService:
    return LabService(session=db)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(session=db)


def get_doctor_service(db: Session = Depends(get_db)) -> DoctorService:
    return DoctorService(session=db)
