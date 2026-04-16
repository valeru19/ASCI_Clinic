from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LabOrderCreateRequest(BaseModel):
    visit_id: str = Field(min_length=36, max_length=36)


class LabOrderResponse(BaseModel):
    id: str
    visit_id: str
    patient_id: str
    ordered_by_doctor_id: str
    status: str
    ordered_at: datetime


class LabOrderItemCreateItem(BaseModel):
    test_type_id: str = Field(min_length=36, max_length=36)
    priority: str = Field(default="normal", pattern=r"^(normal|urgent|stat)$")


class LabOrderItemsCreateRequest(BaseModel):
    items: list[LabOrderItemCreateItem] = Field(min_length=1, max_length=50)


class LabOrderItemResponse(BaseModel):
    id: str
    lab_order_id: str
    test_type_id: str
    priority: str


class LabOrderItemsCreateResponse(BaseModel):
    lab_order_id: str
    created: int
    items: list[LabOrderItemResponse]


class LabResultCreateRequest(BaseModel):
    lab_order_item_id: str = Field(min_length=36, max_length=36)
    value_text: Optional[str] = Field(default=None, max_length=100)
    value_numeric: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None, max_length=30)
    reference_range: Optional[str] = Field(default=None, max_length=50)
    flag: str = Field(pattern=r"^(low|normal|high|critical)$")
    validated_by_doctor_id: str = Field(min_length=36, max_length=36)

    @model_validator(mode="after")
    def validate_value(self) -> "LabResultCreateRequest":
        if self.value_text is None and self.value_numeric is None:
            raise ValueError("Either value_text or value_numeric must be provided")
        return self


class LabResultResponse(BaseModel):
    id: str
    lab_order_item_id: str
    lab_order_id: str
    patient_id: str
    value_text: Optional[str]
    value_numeric: Optional[float]
    unit: Optional[str]
    reference_range: Optional[str]
    flag: Optional[str]
    resulted_at: datetime
    validated_by_doctor_id: Optional[str]


class LabResultListResponse(BaseModel):
    items: list[LabResultResponse]
    total: int
