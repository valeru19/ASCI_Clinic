from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status

from app.api.deps import get_visit_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.visits import (
    DiagnosesCreateRequest,
    DiagnosesCreateResponse,
    GenericCreateResult,
    PrescriptionsCreateRequest,
    ReferralsCreateRequest,
    ReferralsCreateResponse,
    VisitCompleteRequest,
    VisitCreateRequest,
    VisitListResponse,
    VisitResponse,
)
from app.services.visit_service import VisitService

router = APIRouter()


@router.post("/", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def create_visit(
    payload: VisitCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: VisitService = Depends(get_visit_service),
) -> VisitResponse:
    return service.create(payload, current_user)


@router.get("/", response_model=VisitListResponse)
def list_visits(
    doctor_id: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    visit_status: Optional[str] = Query(
        None,
        alias="status",
        pattern="^(in_progress|completed|cancelled)$",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor", "registrar")),
    service: VisitService = Depends(get_visit_service),
) -> VisitListResponse:
    return service.list_visits(
        doctor_id=doctor_id,
        patient_id=patient_id,
        visit_status=visit_status,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/{visit_id}", response_model=VisitResponse)
def get_visit(
    visit_id: str,
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor", "registrar")),
    service: VisitService = Depends(get_visit_service),
) -> VisitResponse:
    return service.get_visit(visit_id, current_user)


@router.patch("/{visit_id}/complete", response_model=VisitResponse)
def complete_visit(
    visit_id: str,
    payload: VisitCompleteRequest | None = Body(default=None),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: VisitService = Depends(get_visit_service),
) -> VisitResponse:
    return service.complete(visit_id, payload or VisitCompleteRequest(), current_user)


@router.post(
    "/{visit_id}/diagnoses",
    response_model=DiagnosesCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_diagnoses(
    visit_id: str,
    payload: DiagnosesCreateRequest = Body(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: VisitService = Depends(get_visit_service),
) -> DiagnosesCreateResponse:
    return service.add_diagnoses(visit_id, payload, current_user)


@router.post(
    "/{visit_id}/prescriptions",
    response_model=GenericCreateResult,
    status_code=status.HTTP_201_CREATED,
)
def add_prescriptions(
    visit_id: str,
    payload: PrescriptionsCreateRequest = Body(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: VisitService = Depends(get_visit_service),
) -> GenericCreateResult:
    return service.add_prescriptions(visit_id, payload, current_user)


@router.post(
    "/{visit_id}/referrals",
    response_model=ReferralsCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_referrals(
    visit_id: str,
    payload: ReferralsCreateRequest = Body(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor")),
    service: VisitService = Depends(get_visit_service),
) -> ReferralsCreateResponse:
    return service.add_referrals(visit_id, payload, current_user)
