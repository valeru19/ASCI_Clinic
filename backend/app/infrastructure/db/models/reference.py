import uuid

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class Specialty(Base):
    __tablename__ = "specialties"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)


class Medication(Base):
    __tablename__ = "medications"
    __table_args__ = {"schema": "clinic"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class ICD10Code(Base):
    __tablename__ = "icd10_codes"
    __table_args__ = {"schema": "clinic"}

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
