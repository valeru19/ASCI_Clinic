import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class Visit(Base):
    __tablename__ = "visits"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    appointment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clinic.appointments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    exam_notes: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    visit_status: Mapped[str] = mapped_column(
        Enum(
            "in_progress",
            "completed",
            "cancelled",
            name="visit_status",
            schema="clinic",
            native_enum=True,
        ),
        nullable=False,
        default="in_progress",
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
