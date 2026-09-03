from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models import PriorityEnum, TicketStatusEnum
from app.schemas.users import UserResponse
from app.schemas.teams import TeamResponse

class TicketBase(BaseModel):
    subject: str
    description: str
    priority: PriorityEnum
    sla_policy_id: UUID
    team_id: Optional[UUID] = None
    assigned_agent_id: Optional[UUID] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[TicketStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assigned_agent_id: Optional[UUID] = None
    team_id: Optional[UUID] = None

class TicketCommentBase(BaseModel):
    body: str
    is_internal_note: bool = False

class TicketCommentCreate(TicketCommentBase):
    pass

class TicketCommentResponse(TicketCommentBase):
    id: UUID
    ticket_id: UUID
    author_id: UUID
    created_at: datetime
    
    model_config = {"from_attributes": True}

class TicketResponse(TicketBase):
    id: UUID
    customer_id: UUID
    status: TicketStatusEnum
    created_at: datetime
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    sla_first_response_due_at: datetime
    sla_resolution_due_at: datetime
    first_response_breached: bool
    resolution_breached: bool

    model_config = {"from_attributes": True}
