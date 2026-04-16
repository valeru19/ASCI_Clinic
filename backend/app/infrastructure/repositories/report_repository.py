from datetime import date, datetime, time

from sqlalchemy import text
from sqlalchemy.orm import Session


def _period_bounds(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    start = datetime.combine(date_from, time.min)
    end = datetime.combine(date_to, time.max)
    return start, end


class SQLAlchemyReportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def doctor_workload(self, *, date_from: date, date_to: date) -> list[dict]:
        start, end = _period_bounds(date_from, date_to)
        rows = self.session.execute(
            text(
                """
                SELECT
                    a.doctor_id::text AS doctor_id,
                    COALESCE(u.username, a.doctor_id::text) AS doctor_name,
                    COUNT(*)::int AS appointments_count,
                    COUNT(*) FILTER (WHERE a.status = 'completed')::int AS completed_count,
                    COUNT(*) FILTER (WHERE a.status = 'cancelled')::int AS cancelled_count
                FROM clinic.appointments a
                LEFT JOIN clinic.doctors d ON d.id = a.doctor_id
                LEFT JOIN clinic.users u ON u.id = d.user_id
                WHERE a.created_at BETWEEN :start AND :end
                GROUP BY a.doctor_id, u.username
                ORDER BY appointments_count DESC, doctor_name ASC
                """
            ),
            {"start": start, "end": end},
        ).mappings()
        return [dict(row) for row in rows]

    def diagnoses_stats(
        self,
        *,
        date_from: date,
        date_to: date,
        limit: int,
    ) -> list[dict]:
        start, end = _period_bounds(date_from, date_to)
        rows = self.session.execute(
            text(
                """
                SELECT
                    d.icd10_code,
                    c.title,
                    COUNT(*)::int AS total
                FROM clinic.diagnoses d
                JOIN clinic.icd10_codes c ON c.code = d.icd10_code
                JOIN clinic.visits v ON v.id = d.visit_id
                JOIN clinic.appointments a ON a.id = v.appointment_id
                WHERE a.created_at BETWEEN :start AND :end
                GROUP BY d.icd10_code, c.title
                ORDER BY total DESC, d.icd10_code ASC
                LIMIT :limit
                """
            ),
            {"start": start, "end": end, "limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def appointments_stats(self, *, date_from: date, date_to: date) -> dict:
        start, end = _period_bounds(date_from, date_to)
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*)::int AS total,
                    COUNT(*) FILTER (WHERE status = 'planned')::int AS planned,
                    COUNT(*) FILTER (WHERE status = 'confirmed')::int AS confirmed,
                    COUNT(*) FILTER (WHERE status = 'completed')::int AS completed,
                    COUNT(*) FILTER (WHERE status = 'cancelled')::int AS cancelled,
                    COUNT(*) FILTER (WHERE status = 'no_show')::int AS no_show
                FROM clinic.appointments
                WHERE created_at BETWEEN :start AND :end
                """
            ),
            {"start": start, "end": end},
        ).mappings().one()
        return dict(row)

    def finance_stats(self, *, date_from: date, date_to: date) -> dict:
        start, end = _period_bounds(date_from, date_to)
        row = self.session.execute(
            text(
                """
                SELECT
                    COUNT(*)::int AS invoices_count,
                    COALESCE(SUM(total_amount), 0)::numeric AS total_amount,
                    COALESCE(SUM(total_amount) FILTER (WHERE status = 'paid'), 0)::numeric AS paid_amount,
                    COALESCE(SUM(total_amount) FILTER (WHERE status = 'issued'), 0)::numeric AS issued_amount
                FROM clinic.invoices
                WHERE issued_at BETWEEN :start AND :end
                """
            ),
            {"start": start, "end": end},
        ).mappings().one()
        return dict(row)
