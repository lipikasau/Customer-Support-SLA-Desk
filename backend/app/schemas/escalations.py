from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class EscalationResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    escalated_to: UUID
    reason: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
