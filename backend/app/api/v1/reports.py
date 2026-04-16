from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_report_service, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.reports import (
    AppointmentsStatsResponse,
    DiagnosesStatsResponse,
    DoctorWorkloadResponse,
    FinanceStatsResponse,
)
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/doctor-workload", response_model=DoctorWorkloadResponse)
def doctor_workload(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: ReportService = Depends(get_report_service),
) -> DoctorWorkloadResponse:
    return service.doctor_workload(
        date_from=date_from,
        date_to=date_to,
        current_user=current_user,
    )


@router.get("/diagnoses", response_model=DiagnosesStatsResponse)
def diagnoses_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    limit: int = Query(20, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "doctor", "registrar")),
    service: ReportService = Depends(get_report_service),
) -> DiagnosesStatsResponse:
    return service.diagnoses_stats(
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        current_user=current_user,
    )


@router.get("/appointments", response_model=AppointmentsStatsResponse)
def appointments_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin", "registrar")),
    service: ReportService = Depends(get_report_service),
) -> AppointmentsStatsResponse:
    return service.appointments_stats(
        date_from=date_from,
        date_to=date_to,
        current_user=current_user,
    )


@router.get("/finance", response_model=FinanceStatsResponse)
def finance_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: CurrentUserResponse = Depends(require_roles("admin")),
    service: ReportService = Depends(get_report_service),
) -> FinanceStatsResponse:
    return service.finance_stats(
        date_from=date_from,
        date_to=date_to,
        current_user=current_user,
    )
