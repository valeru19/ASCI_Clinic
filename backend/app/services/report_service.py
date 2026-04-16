from datetime import date

from sqlalchemy.orm import Session

from app.infrastructure.repositories.report_repository import SQLAlchemyReportRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.reports import (
    AppointmentsStatsResponse,
    DiagnosesStatsItem,
    DiagnosesStatsResponse,
    DoctorWorkloadItem,
    DoctorWorkloadResponse,
    FinanceStatsResponse,
)


class ReportService:
    """Application service for analytics and reporting use cases."""

    def __init__(self, session: Session) -> None:
        self.repo = SQLAlchemyReportRepository(session)

    def doctor_workload(
        self,
        *,
        date_from: date,
        date_to: date,
        current_user: CurrentUserResponse,
    ) -> DoctorWorkloadResponse:
        rows = self.repo.doctor_workload(date_from=date_from, date_to=date_to)
        return DoctorWorkloadResponse(
            items=[
                DoctorWorkloadItem(
                    doctor_id=row["doctor_id"],
                    doctor_name=row["doctor_name"],
                    appointments_count=row["appointments_count"],
                    completed_count=row["completed_count"],
                    cancelled_count=row["cancelled_count"],
                )
                for row in rows
            ]
        )

    def diagnoses_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> DiagnosesStatsResponse:
        rows = self.repo.diagnoses_stats(date_from=date_from, date_to=date_to, limit=limit)
        return DiagnosesStatsResponse(
            date_from=date_from,
            date_to=date_to,
            items=[
                DiagnosesStatsItem(
                    icd10_code=row["icd10_code"],
                    title=row["title"],
                    total=row["total"],
                )
                for row in rows
            ],
        )

    def appointments_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        current_user: CurrentUserResponse,
    ) -> AppointmentsStatsResponse:
        row = self.repo.appointments_stats(date_from=date_from, date_to=date_to)
        return AppointmentsStatsResponse(
            date_from=date_from,
            date_to=date_to,
            total=row["total"],
            planned=row["planned"],
            confirmed=row["confirmed"],
            completed=row["completed"],
            cancelled=row["cancelled"],
            no_show=row["no_show"],
        )

    def finance_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        current_user: CurrentUserResponse,
    ) -> FinanceStatsResponse:
        row = self.repo.finance_stats(date_from=date_from, date_to=date_to)
        return FinanceStatsResponse(
            date_from=date_from,
            date_to=date_to,
            invoices_count=row["invoices_count"],
            total_amount=float(row["total_amount"]),
            paid_amount=float(row["paid_amount"]),
            issued_amount=float(row["issued_amount"]),
        )

