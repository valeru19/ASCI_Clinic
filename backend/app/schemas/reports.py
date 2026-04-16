from datetime import date

from pydantic import BaseModel, Field


class DoctorWorkloadItem(BaseModel):
    doctor_id: str
    doctor_name: str
    appointments_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    cancelled_count: int = Field(ge=0)


class DoctorWorkloadResponse(BaseModel):
    items: list[DoctorWorkloadItem]


class DiagnosesStatsItem(BaseModel):
    icd10_code: str
    title: str
    total: int = Field(ge=0)


class DiagnosesStatsResponse(BaseModel):
    date_from: date
    date_to: date
    items: list[DiagnosesStatsItem]


class AppointmentsStatsResponse(BaseModel):
    date_from: date
    date_to: date
    total: int = Field(ge=0)
    planned: int = Field(ge=0)
    confirmed: int = Field(ge=0)
    completed: int = Field(ge=0)
    cancelled: int = Field(ge=0)
    no_show: int = Field(ge=0)


class FinanceStatsResponse(BaseModel):
    date_from: date
    date_to: date
    invoices_count: int = Field(ge=0)
    total_amount: float = Field(ge=0)
    paid_amount: float = Field(ge=0)
    issued_amount: float = Field(ge=0)
