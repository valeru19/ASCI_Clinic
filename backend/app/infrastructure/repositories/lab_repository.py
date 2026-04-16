import uuid

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.infrastructure.db.models.lab import LabOrder, LabOrderItem, LabResult


class SQLAlchemyLabRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def visit_context(self, visit_id: str) -> tuple[str, str] | None:
        try:
            vid = str(uuid.UUID(visit_id))
        except ValueError:
            return None
        row = self.session.execute(
            text(
                """
                SELECT a.patient_id::text AS patient_id, a.doctor_id::text AS doctor_id
                FROM clinic.visits v
                JOIN clinic.appointments a ON a.id = v.appointment_id
                WHERE v.id = :visit_id
                LIMIT 1
                """
            ),
            {"visit_id": vid},
        ).first()
        if not row:
            return None
        return str(row[0]), str(row[1])

    def create_order(self, order: LabOrder) -> LabOrder:
        self.session.add(order)
        self.session.flush()
        self.session.refresh(order)
        return order

    def get_order(self, order_id: str) -> LabOrder | None:
        try:
            oid = uuid.UUID(order_id)
        except ValueError:
            return None
        stmt = select(LabOrder).where(LabOrder.id == oid)
        return self.session.execute(stmt).scalar_one_or_none()

    def test_type_exists(self, test_type_id: str) -> bool:
        try:
            tid = str(uuid.UUID(test_type_id))
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.lab_test_types WHERE id = :test_type_id LIMIT 1"),
            {"test_type_id": tid},
        ).first()
        return row is not None

    def create_order_items(self, items: list[LabOrderItem]) -> list[LabOrderItem]:
        self.session.add_all(items)
        self.session.flush()
        for item in items:
            self.session.refresh(item)
        return items

    def get_order_item(self, item_id: str) -> LabOrderItem | None:
        try:
            iid = uuid.UUID(item_id)
        except ValueError:
            return None
        stmt = select(LabOrderItem).where(LabOrderItem.id == iid)
        return self.session.execute(stmt).scalar_one_or_none()

    def doctor_exists(self, doctor_id: str) -> bool:
        try:
            did = str(uuid.UUID(doctor_id))
        except ValueError:
            return False
        row = self.session.execute(
            text("SELECT 1 FROM clinic.doctors WHERE id = :doctor_id LIMIT 1"),
            {"doctor_id": did},
        ).first()
        return row is not None

    def has_result_for_order_item(self, order_item_id: str) -> bool:
        try:
            iid = uuid.UUID(order_item_id)
        except ValueError:
            return False
        stmt = select(func.count(LabResult.id)).where(LabResult.lab_order_item_id == iid)
        return int(self.session.execute(stmt).scalar_one()) > 0

    def create_result(self, result: LabResult) -> LabResult:
        self.session.add(result)
        self.session.flush()
        self.session.refresh(result)
        return result

    def list_results(
        self,
        *,
        patient_id: str | None,
        order_id: str | None,
        skip: int,
        limit: int,
    ) -> list[tuple[LabResult, str, str]]:
        stmt = (
            select(LabResult, LabOrder.id, LabOrder.patient_id)
            .join(LabOrderItem, LabOrderItem.id == LabResult.lab_order_item_id)
            .join(LabOrder, LabOrder.id == LabOrderItem.lab_order_id)
            .order_by(LabResult.resulted_at.desc())
        )
        if patient_id:
            try:
                stmt = stmt.where(LabOrder.patient_id == uuid.UUID(patient_id))
            except ValueError:
                return []
        if order_id:
            try:
                stmt = stmt.where(LabOrder.id == uuid.UUID(order_id))
            except ValueError:
                return []

        rows = self.session.execute(stmt.offset(skip).limit(limit)).all()
        return [(row[0], str(row[1]), str(row[2])) for row in rows]

    def count_results(self, *, patient_id: str | None, order_id: str | None) -> int:
        stmt = (
            select(func.count(LabResult.id))
            .select_from(LabResult)
            .join(LabOrderItem, LabOrderItem.id == LabResult.lab_order_item_id)
            .join(LabOrder, LabOrder.id == LabOrderItem.lab_order_id)
        )
        if patient_id:
            try:
                stmt = stmt.where(LabOrder.patient_id == uuid.UUID(patient_id))
            except ValueError:
                return 0
        if order_id:
            try:
                stmt = stmt.where(LabOrder.id == uuid.UUID(order_id))
            except ValueError:
                return 0
        return int(self.session.execute(stmt).scalar_one())
