from fastapi import APIRouter, Depends

from app.api.deps import get_doctor_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.specialties import SpecialtyItem, SpecialtyListResponse
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.get("/", response_model=SpecialtyListResponse)
def list_specialties(
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor", "registrar")),
    service: DoctorService = Depends(get_doctor_service),
) -> SpecialtyListResponse:
    rows = service.list_specialties()
    return SpecialtyListResponse(
        items=[SpecialtyItem(**row) for row in rows],
        total=len(rows),
    )
