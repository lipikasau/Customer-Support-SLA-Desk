from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List

from app.api.deps import DbSession, CurrentUser, get_current_active_manager
from app.crud.escalations import get_escalations, get_escalation, resolve_escalation
from app.schemas.escalations import EscalationResponse
from app.models import User

router = APIRouter()

@router.get("/", response_model=List[EscalationResponse])
async def read_escalations(
    db: DbSession,
    current_user: User = Depends(get_current_active_manager)
):
    escalations = await get_escalations(db)
    return escalations

@router.post("/{escalation_id}/resolve", response_model=EscalationResponse)
async def resolve_existing_escalation(
    escalation_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_active_manager)
):
    escalation = await get_escalation(db, escalation_id=escalation_id)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    escalation = await resolve_escalation(db, escalation)
    return escalation
