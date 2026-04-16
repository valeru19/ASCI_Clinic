from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VisitCreateRequest(BaseModel):
    appointment_id: str = Field(min_length=36, max_length=36)
    chief_complaint: str = Field(min_length=1, max_length=4000)
    exam_notes: str = Field(min_length=1, max_length=10000)
    treatment_plan: Optional[str] = Field(default=None, max_length=10000)


class VisitCompleteRequest(BaseModel):
    treatment_plan: Optional[str] = Field(default=None, max_length=10000)


class VisitResponse(BaseModel):
    id: str
    appointment_id: str
    patient_id: str
    patient_full_name: str
    doctor_id: str
    doctor_full_name: str
    chief_complaint: str
    exam_notes: str
    treatment_plan: Optional[str]
    visit_status: str
    closed_at: Optional[datetime]


class VisitListResponse(BaseModel):
    items: list[VisitResponse]
    total: int


class DiagnosisCreateItem(BaseModel):
    icd10_code: str = Field(
        min_length=3,
        max_length=10,
        pattern=r"^[A-Z][0-9]{2}(\.[0-9A-Z]{1,2})?$",
    )
    is_primary: bool = Field(default=False)
    comment: Optional[str] = Field(default=None, max_length=2000)


class DiagnosesCreateRequest(BaseModel):
    items: list[DiagnosisCreateItem] = Field(min_length=1, max_length=50)


class DiagnosisResponse(BaseModel):
    id: str
    icd10_code: str
    is_primary: bool
    comment: Optional[str]


class DiagnosesCreateResponse(BaseModel):
    visit_id: str
    created: int
    diagnoses: list[DiagnosisResponse]


class PrescriptionCreateItem(BaseModel):
    medication_id: str = Field(min_length=36, max_length=36)
    dosage: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^\d+(\.\d+)?\s?(mg|ml|g|mcg)$",
    )
    frequency: str = Field(min_length=1, max_length=100)
    duration_days: int = Field(ge=1, le=365)
    instructions: Optional[str] = Field(default=None, max_length=2000)


class PrescriptionsCreateRequest(BaseModel):
    items: list[PrescriptionCreateItem] = Field(min_length=1, max_length=50)


class GenericCreateResult(BaseModel):
    visit_id: str
    created: int


class ReferralCreateItem(BaseModel):
    target_specialty_id: int = Field(ge=1)
    target_doctor_id: Optional[str] = Field(default=None, min_length=36, max_length=36)
    reason: str = Field(min_length=1, max_length=2000)
    comment: Optional[str] = Field(default=None, max_length=2000)


class ReferralsCreateRequest(BaseModel):
    items: list[ReferralCreateItem] = Field(min_length=1, max_length=50)


class ReferralResponse(BaseModel):
    id: str
    target_specialty_id: int
    target_doctor_id: Optional[str]
    reason: str
    status: str
    comment: Optional[str]
    created_at: datetime


class ReferralsCreateResponse(BaseModel):
    visit_id: str
    created: int
    referrals: list[ReferralResponse]
