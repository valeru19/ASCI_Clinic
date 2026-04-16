from pydantic import BaseModel


class SpecialtyItem(BaseModel):
    id: int
    name: str


class SpecialtyListResponse(BaseModel):
    items: list[SpecialtyItem]
    total: int
