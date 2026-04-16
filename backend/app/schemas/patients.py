from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreateRequest(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    birth_date: date
    gender: str = Field(pattern="^[MFO]$")
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[0-9\-\(\)\s]{7,20}$",
    )
    email: Optional[EmailStr] = None
    insurance_number: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)


class PatientUpdateRequest(BaseModel):
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(default=None, pattern="^[MFO]$")
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[0-9\-\(\)\s]{7,20}$",
    )
    email: Optional[EmailStr] = None
    insurance_number: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    birth_date: date
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    insurance_number: Optional[str] = None
    address: Optional[str] = None
    is_active: bool


class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
