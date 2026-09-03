from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models import SLAPolicy
from app.schemas.sla_policies import SLAPolicyCreate, SLAPolicyUpdate

async def get_sla_policy(db: AsyncSession, policy_id: UUID) -> SLAPolicy | None:
    result = await db.execute(select(SLAPolicy).where(SLAPolicy.id == policy_id))
    return result.scalars().first()

async def get_sla_policies(db: AsyncSession) -> list[SLAPolicy]:
    result = await db.execute(select(SLAPolicy))
    return list(result.scalars().all())

async def create_sla_policy(db: AsyncSession, policy_in: SLAPolicyCreate) -> SLAPolicy:
    db_policy = SLAPolicy(
        name=policy_in.name,
        priority=policy_in.priority,
        first_response_minutes=policy_in.first_response_minutes,
        resolution_minutes=policy_in.resolution_minutes,
        business_hours_only=policy_in.business_hours_only
    )
    db.add(db_policy)
    await db.commit()
    await db.refresh(db_policy)
    return db_policy

async def update_sla_policy(db: AsyncSession, db_policy: SLAPolicy, policy_in: SLAPolicyUpdate) -> SLAPolicy:
    update_data = policy_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_policy, field, update_data[field])
    await db.commit()
    await db.refresh(db_policy)
    return db_policy
