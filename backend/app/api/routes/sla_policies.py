from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List

from app.api.deps import DbSession, CurrentUser, get_current_active_admin
from app.crud.sla_policies import get_sla_policies, get_sla_policy, create_sla_policy, update_sla_policy
from app.schemas.sla_policies import SLAPolicyCreate, SLAPolicyUpdate, SLAPolicyResponse
from app.models import User

router = APIRouter()

@router.post("/", response_model=SLAPolicyResponse)
async def create_new_sla_policy(
    policy_in: SLAPolicyCreate,
    db: DbSession,
    current_user: User = Depends(get_current_active_admin)
):
    policy = await create_sla_policy(db, policy_in)
    return policy

@router.get("/", response_model=List[SLAPolicyResponse])
async def read_sla_policies(
    db: DbSession,
    current_user: CurrentUser
):
    policies = await get_sla_policies(db)
    return policies

@router.patch("/{policy_id}", response_model=SLAPolicyResponse)
async def update_existing_sla_policy(
    policy_id: UUID,
    policy_in: SLAPolicyUpdate,
    db: DbSession,
    current_user: User = Depends(get_current_active_admin)
):
    policy = await get_sla_policy(db, policy_id=policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="SLA Policy not found")
    
    policy = await update_sla_policy(db, db_policy=policy, policy_in=policy_in)
    return policy
