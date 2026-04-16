from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentCreateRequest(BaseModel):
    patient_id: str = Field(min_length=36, max_length=36)
    doctor_id: str = Field(min_length=36, max_length=36)
    slot_id: str = Field(min_length=36, max_length=36)
    reason: Optional[str] = Field(default=None, max_length=2000)


class AppointmentRescheduleRequest(BaseModel):
    slot_id: str = Field(min_length=36, max_length=36)


class AppointmentCancelRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    patient_full_name: str | None = None
    doctor_id: str
    doctor_full_name: str | None = None
    slot_id: str
    status: str
    created_at: datetime


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
