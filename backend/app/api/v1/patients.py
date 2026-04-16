from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_patient_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.patients import (
    PatientCreateRequest,
    PatientListResponse,
    PatientResponse,
    PatientUpdateRequest,
)
from app.services.patient_service import PatientService

router = APIRouter()


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    payload: PatientCreateRequest,
    _: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    return service.create(payload, _)


@router.get("/", response_model=PatientListResponse)
def list_patients(
    q: Optional[str] = Query(None, max_length=255),
    birth_date: Optional[date] = None,
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(
        require_roles("admin", "doctor", "registrar")
    ),
    service: PatientService = Depends(get_patient_service),
) -> PatientListResponse:
    return service.list_patients(
        q=q,
        birth_date=birth_date,
        include_inactive=include_inactive,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    _: CurrentUserResponse = Depends(require_roles("admin", "doctor", "registrar")),
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    return service.get_patient(patient_id, _)


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    payload: PatientUpdateRequest,
    _: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    return service.update_patient(patient_id, payload, _)


@router.delete("/{patient_id}", response_model=PatientResponse)
def deactivate_patient(
    patient_id: str,
    _: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: PatientService = Depends(get_patient_service),
) -> PatientResponse:
    return service.soft_delete(patient_id, _)
