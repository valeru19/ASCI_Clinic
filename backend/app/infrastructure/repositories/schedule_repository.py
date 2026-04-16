import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, exists, func, select, text
from sqlalchemy.orm import Session

from app.infrastructure.db.models.schedule import Schedule, ScheduleException, ScheduleSlot


class SQLAlchemyScheduleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def doctor_exists(self, doctor_id: str) -> bool:
        try:
            did = uuid.UUID(doctor_id)
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.doctors WHERE id = :doctor_id LIMIT 1"),
            {"doctor_id": str(did)},
        ).first()
        return row is not None

    def has_overlap(
        self,
        *,
        doctor_id: str,
        weekday: int,
        start_time,
        end_time,
    ) -> bool:
        did = uuid.UUID(doctor_id)
        stmt = (
            select(exists().where(
                and_(
                    Schedule.doctor_id == did,
                    Schedule.weekday == weekday,
                    Schedule.is_active.is_(True),
                    Schedule.start_time < end_time,
                    Schedule.end_time > start_time,
                )
            ))
            .select_from(Schedule)
        )
        return bool(self.session.execute(stmt).scalar())

    def create_schedule(self, schedule: Schedule) -> Schedule:
        self.session.add(schedule)
        self.session.flush()
        self.session.refresh(schedule)
        return schedule

    def get_schedule(self, schedule_id: str) -> Schedule | None:
        try:
            sid = uuid.UUID(schedule_id)
        except ValueError:
            return None
        stmt = select(Schedule).where(Schedule.id == sid)
        return self.session.execute(stmt).scalar_one_or_none()

    def count_schedules(
        self,
        *,
        doctor_id: str | None,
        weekday: int | None,
        include_inactive: bool,
    ) -> int:
        stmt = select(func.count(Schedule.id)).select_from(Schedule)
        if doctor_id:
            try:
                stmt = stmt.where(Schedule.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return 0
        if weekday:
            stmt = stmt.where(Schedule.weekday == weekday)
        if not include_inactive:
            stmt = stmt.where(Schedule.is_active.is_(True))
        return int(self.session.execute(stmt).scalar_one())

    def list_schedules(
        self,
        *,
        doctor_id: str | None,
        weekday: int | None,
        include_inactive: bool,
        skip: int,
        limit: int,
    ) -> list[Schedule]:
        stmt = select(Schedule)
        if doctor_id:
            try:
                stmt = stmt.where(Schedule.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return []
        if weekday:
            stmt = stmt.where(Schedule.weekday == weekday)
        if not include_inactive:
            stmt = stmt.where(Schedule.is_active.is_(True))
        stmt = stmt.order_by(Schedule.doctor_id, Schedule.weekday, Schedule.start_time)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def generate_slots(
        self,
        *,
        schedule: Schedule,
        date_from: date,
        date_to: date,
    ) -> list[ScheduleSlot]:
        created_slots: list[ScheduleSlot] = []
        current = date_from

        existing_stmt = select(ScheduleSlot.start_at).where(
            and_(
                ScheduleSlot.schedule_id == schedule.id,
                ScheduleSlot.start_at >= datetime.combine(date_from, schedule.start_time).replace(tzinfo=UTC),
                ScheduleSlot.start_at <= datetime.combine(date_to, schedule.end_time).replace(tzinfo=UTC),
            )
        )
        existing = {row[0] for row in self.session.execute(existing_stmt).all()}

        slot_delta = timedelta(minutes=schedule.slot_minutes)

        while current <= date_to:
            if current.isoweekday() == schedule.weekday:
                slot_start = datetime.combine(current, schedule.start_time).replace(
                    tzinfo=UTC
                )
                day_end = datetime.combine(current, schedule.end_time).replace(
                    tzinfo=UTC
                )
                while slot_start + slot_delta <= day_end:
                    if slot_start not in existing:
                        slot = ScheduleSlot(
                            schedule_id=schedule.id,
                            start_at=slot_start,
                            end_at=slot_start + slot_delta,
                            status="available",
                        )
                        self.session.add(slot)
                        created_slots.append(slot)
                    slot_start += slot_delta
            current += timedelta(days=1)

        self.session.flush()
        for slot in created_slots:
            self.session.refresh(slot)
        return created_slots

    def create_exception(self, exc: ScheduleException) -> ScheduleException:
        self.session.add(exc)
        self.session.flush()
        self.session.refresh(exc)
        return exc

    def count_slots(
        self,
        *,
        doctor_id: str | None,
        date_from: date,
        date_to: date,
        status: str | None,
    ) -> int:
        start = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=UTC)
        end = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=UTC)
        stmt = (
            select(func.count(ScheduleSlot.id))
            .join(Schedule, Schedule.id == ScheduleSlot.schedule_id)
            .where(
                and_(
                    ScheduleSlot.start_at >= start,
                    ScheduleSlot.end_at <= end,
                )
            )
        )
        if doctor_id:
            try:
                stmt = stmt.where(Schedule.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return 0
        if status:
            stmt = stmt.where(ScheduleSlot.status == status)
        return int(self.session.execute(stmt).scalar_one())

    def list_slots(
        self,
        *,
        doctor_id: str | None,
        date_from: date,
        date_to: date,
        status: str | None,
        skip: int,
        limit: int,
    ) -> list[ScheduleSlot]:
        start = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=UTC)
        end = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=UTC)
        stmt = (
            select(ScheduleSlot)
            .join(Schedule, Schedule.id == ScheduleSlot.schedule_id)
            .where(
                and_(
                    ScheduleSlot.start_at >= start,
                    ScheduleSlot.end_at <= end,
                )
            )
        )
        if doctor_id:
            try:
                stmt = stmt.where(Schedule.doctor_id == uuid.UUID(doctor_id))
            except ValueError:
                return []
        if status:
            stmt = stmt.where(ScheduleSlot.status == status)

        stmt = stmt.order_by(ScheduleSlot.start_at.asc()).offset(skip).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
