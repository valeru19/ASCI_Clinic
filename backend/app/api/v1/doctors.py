from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_doctor_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.doctors import (
    DoctorCreateRequest,
    DoctorEmploymentUpdateRequest,
    DoctorListItem,
    DoctorListResponse,
)
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.post("/", response_model=DoctorListItem, status_code=status.HTTP_201_CREATED)
def create_doctor(
    payload: DoctorCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorListItem:
    return service.create_doctor(payload, current_user)


@router.get("/", response_model=DoctorListResponse)
def list_doctors(
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorListResponse:
    return service.list_doctors(
        include_inactive=include_inactive,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.patch("/{doctor_id}/employment", response_model=DoctorListItem)
def update_doctor_employment(
    doctor_id: str,
    payload: DoctorEmploymentUpdateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin")),
    service: DoctorService = Depends(get_doctor_service),
) -> DoctorListItem:
    return service.update_employment(doctor_id, payload, current_user)
