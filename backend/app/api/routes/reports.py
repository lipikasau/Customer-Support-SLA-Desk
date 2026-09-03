from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone

from app.api.deps import DbSession, CurrentUser, get_current_active_manager
from app.models import Ticket, User, RoleEnum

router = APIRouter()

@router.get("/sla-compliance")
async def sla_compliance(
    db: DbSession,
    current_user: User = Depends(get_current_active_manager),
    days: int = 30
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.count(Ticket.id).label("total_tickets"),
            func.sum(
                func.cast(Ticket.first_response_breached == False, func.integer())
            ).label("first_response_met"),
            func.sum(
                func.cast(Ticket.resolution_breached == False, func.integer())
            ).label("resolution_met")
        ).where(Ticket.created_at >= cutoff)
    )
    stats = result.first()
    
    total = stats.total_tickets or 0
    fr_met = stats.first_response_met or 0
    res_met = stats.resolution_met or 0
    
    return {
        "total_tickets": total,
        "first_response_met_percentage": (fr_met / total * 100) if total > 0 else 0,
        "resolution_met_percentage": (res_met / total * 100) if total > 0 else 0
    }
