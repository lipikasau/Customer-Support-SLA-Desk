import asyncio
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models import Ticket, TicketStatusEnum, Escalation, User, RoleEnum
from app.crud.tickets import add_ticket_event

celery_app = Celery(
    "sla_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.beat_schedule = {
    'check-sla-breaches-every-minute': {
        'task': 'app.worker.check_sla_breaches',
        'schedule': crontab(minute='*'), # Run every minute
    },
}
celery_app.conf.timezone = 'UTC'

async def async_check_sla_breaches():
    engine = create_async_engine(settings.async_database_uri)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    now = datetime.now(timezone.utc)
    
    async with async_session() as db:
        # Find all open tickets
        result = await db.execute(select(Ticket).where(Ticket.status.in_([TicketStatusEnum.open, TicketStatusEnum.in_progress])))
        open_tickets = result.scalars().all()
        
        # Get a manager to assign escalations to
        # In a real app we'd find the manager of the ticket's team
        manager_result = await db.execute(select(User).where(User.role == RoleEnum.manager))
        manager = manager_result.scalars().first()
        
        for ticket in open_tickets:
            # Check First Response SLA
            if not ticket.first_responded_at and not ticket.first_response_breached:
                if now > ticket.sla_first_response_due_at:
                    ticket.first_response_breached = True
                    await add_ticket_event(db, ticket.id, None, "sla_breached", {"type": "first_response_auto_check"})
                    
                    if manager:
                        escalation = Escalation(
                            ticket_id=ticket.id,
                            escalated_to=manager.id,
                            reason="first_response_sla_breached"
                        )
                        db.add(escalation)

            # Check Resolution SLA
            if not ticket.resolved_at and not ticket.resolution_breached:
                if now > ticket.sla_resolution_due_at:
                    ticket.resolution_breached = True
                    await add_ticket_event(db, ticket.id, None, "sla_breached", {"type": "resolution_auto_check"})
                    
                    if manager:
                        escalation = Escalation(
                            ticket_id=ticket.id,
                            escalated_to=manager.id,
                            reason="resolution_sla_breached"
                        )
                        db.add(escalation)
                        
        await db.commit()
    await engine.dispose()

@celery_app.task
def check_sla_breaches():
    asyncio.run(async_check_sla_breaches())
