from pydantic import BaseModel, EmailStr, Field


class DoctorListItem(BaseModel):
    id: str
    username: str | None
    email: str | None
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    full_name: str
    license_number: str
    experience_years: int
    specializations: list[str]
    monthly_salary: float
    bonus_percent: float
    is_active: bool


class DoctorListResponse(BaseModel):
    items: list[DoctorListItem]
    total: int


class DoctorCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    license_number: str = Field(min_length=3, max_length=50)
    experience_years: int = Field(ge=0, le=60)
    specialty_ids: list[int] = Field(default_factory=list, max_length=10)
    monthly_salary: float = Field(default=0, ge=0, le=10_000_000)
    bonus_percent: float = Field(default=0, ge=0, le=100)
    is_active: bool = True


class DoctorEmploymentUpdateRequest(BaseModel):
    monthly_salary: float | None = Field(default=None, ge=0, le=10_000_000)
    bonus_percent: float | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None
