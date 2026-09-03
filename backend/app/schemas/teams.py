from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class TeamMemberAdd(BaseModel):
    user_id: UUID
