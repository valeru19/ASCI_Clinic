import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class LabTestType(Base):
    __tablename__ = "lab_test_types"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(100), nullable=True)


class LabOrder(Base):
    __tablename__ = "lab_orders"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    visit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.visits.id", ondelete="CASCADE"),
        nullable=False,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.patients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ordered_by_doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.doctors.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "created",
            "in_progress",
            "completed",
            "cancelled",
            name="lab_order_status",
            schema="clinic",
            native_enum=True,
        ),
        nullable=False,
        default="created",
    )
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class LabOrderItem(Base):
    __tablename__ = "lab_order_items"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lab_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.lab_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.lab_test_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")


class LabResult(Base):
    __tablename__ = "lab_results"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lab_order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.lab_order_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    value_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value_numeric: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    flag: Mapped[str | None] = mapped_column(String(10), nullable=True)
    resulted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    validated_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.doctors.id", ondelete="SET NULL"),
        nullable=True,
    )
