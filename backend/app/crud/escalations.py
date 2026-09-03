from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone

from app.models import Escalation
from app.schemas.escalations import EscalationResponse

async def get_escalations(db: AsyncSession) -> list[Escalation]:
    result = await db.execute(select(Escalation))
    return list(result.scalars().all())

async def get_escalation(db: AsyncSession, escalation_id: UUID) -> Escalation | None:
    result = await db.execute(select(Escalation).where(Escalation.id == escalation_id))
    return result.scalars().first()

async def resolve_escalation(db: AsyncSession, escalation: Escalation) -> Escalation:
    escalation.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(escalation)
    return escalation
