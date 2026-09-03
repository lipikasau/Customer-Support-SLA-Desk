from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from app.models import PriorityEnum

class SLAPolicyBase(BaseModel):
    name: str
    priority: PriorityEnum
    first_response_minutes: int
    resolution_minutes: int
    business_hours_only: bool = True

class SLAPolicyCreate(SLAPolicyBase):
    pass

class SLAPolicyUpdate(BaseModel):
    name: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    first_response_minutes: Optional[int] = None
    resolution_minutes: Optional[int] = None
    business_hours_only: Optional[bool] = None

class SLAPolicyResponse(SLAPolicyBase):
    id: UUID

    model_config = {"from_attributes": True}
