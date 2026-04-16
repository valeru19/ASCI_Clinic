from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreateRequest(BaseModel):
    doctor_id: str = Field(min_length=36, max_length=36)
    weekday: int = Field(ge=1, le=7)
    start_time: time
    end_time: time
    slot_minutes: int = Field(ge=15, le=60)
    is_active: bool = True


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doctor_id: str
    weekday: int
    start_time: time
    end_time: time
    slot_minutes: int
    is_active: bool


class ScheduleListResponse(BaseModel):
    items: list[ScheduleResponse]
    total: int


class ScheduleSlotGenerateRequest(BaseModel):
    schedule_id: str = Field(min_length=36, max_length=36)
    date_from: date
    date_to: date


class ScheduleSlotResponse(BaseModel):
    id: str
    schedule_id: str
    start_at: datetime
    end_at: datetime
    status: str


class ScheduleSlotGenerateResponse(BaseModel):
    created: int
    slots: list[ScheduleSlotResponse]


class ScheduleSlotListResponse(BaseModel):
    items: list[ScheduleSlotResponse]
    total: int


class ScheduleExceptionCreateRequest(BaseModel):
    doctor_id: str = Field(min_length=36, max_length=36)
    date_from: date
    date_to: date
    reason: str = Field(min_length=3, max_length=255)


class ScheduleExceptionResponse(BaseModel):
    id: str
    doctor_id: str
    date_from: date
    date_to: date
    reason: str
