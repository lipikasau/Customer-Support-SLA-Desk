from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from datetime import datetime, timezone

from app.models import Ticket, TicketComment, TicketEvent, SLAPolicy, TicketStatusEnum, User
from app.schemas.tickets import TicketCreate, TicketUpdate, TicketCommentCreate
from app.core.sla import add_business_minutes

async def get_ticket(db: AsyncSession, ticket_id: UUID) -> Ticket | None:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalars().first()

async def get_tickets(db: AsyncSession) -> list[Ticket]:
    result = await db.execute(select(Ticket))
    return list(result.scalars().all())

async def create_ticket(db: AsyncSession, ticket_in: TicketCreate, customer_id: UUID) -> Ticket:
    # 1. Fetch SLA policy
    policy_result = await db.execute(select(SLAPolicy).where(SLAPolicy.id == ticket_in.sla_policy_id))
    policy = policy_result.scalars().first()
    if not policy:
        raise ValueError("SLA Policy not found")
        
    now = datetime.now(timezone.utc)
    
    # 2. Compute due dates
    if policy.business_hours_only:
        first_resp_due = add_business_minutes(now, policy.first_response_minutes)
        resolution_due = add_business_minutes(now, policy.resolution_minutes)
    else:
        from datetime import timedelta
        first_resp_due = now + timedelta(minutes=policy.first_response_minutes)
        resolution_due = now + timedelta(minutes=policy.resolution_minutes)
        
    db_ticket = Ticket(
        subject=ticket_in.subject,
        description=ticket_in.description,
        customer_id=customer_id,
        assigned_agent_id=ticket_in.assigned_agent_id,
        team_id=ticket_in.team_id,
        priority=ticket_in.priority,
        sla_policy_id=ticket_in.sla_policy_id,
        sla_first_response_due_at=first_resp_due,
        sla_resolution_due_at=resolution_due,
        created_at=now
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    
    # Add audit event
    await add_ticket_event(db, db_ticket.id, customer_id, "ticket_created", {"status": "open"})
    
    return db_ticket

async def update_ticket(db: AsyncSession, ticket: Ticket, ticket_in: TicketUpdate, actor_id: UUID) -> Ticket:
    update_data = ticket_in.model_dump(exclude_unset=True)
    
    old_status = ticket.status
    now = datetime.now(timezone.utc)
    
    for field in update_data:
        setattr(ticket, field, update_data[field])
        
    # Status change logic
    if "status" in update_data and old_status != update_data["status"]:
        if update_data["status"] == TicketStatusEnum.resolved:
            ticket.resolved_at = now
            if now > ticket.sla_resolution_due_at:
                ticket.resolution_breached = True
        
        await add_ticket_event(db, ticket.id, actor_id, "status_changed", {"from": old_status.value, "to": update_data["status"].value})
        
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def add_ticket_comment(db: AsyncSession, ticket: Ticket, comment_in: TicketCommentCreate, author: User) -> TicketComment:
    db_comment = TicketComment(
        ticket_id=ticket.id,
        author_id=author.id,
        body=comment_in.body,
        is_internal_note=comment_in.is_internal_note
    )
    db.add(db_comment)
    
    now = datetime.now(timezone.utc)
    
    # Check if this is the first response by an agent
    if author.role.value in ["agent", "manager", "admin"] and not comment_in.is_internal_note:
        if not ticket.first_responded_at:
            ticket.first_responded_at = now
            if now > ticket.sla_first_response_due_at:
                ticket.first_response_breached = True
                await add_ticket_event(db, ticket.id, author.id, "sla_breached", {"type": "first_response"})
    
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def add_ticket_event(db: AsyncSession, ticket_id: UUID, actor_id: UUID, event_type: str, metadata: dict = None) -> TicketEvent:
    event = TicketEvent(
        ticket_id=ticket_id,
        actor_id=actor_id,
        event_type=event_type,
        metadata_=metadata
    )
    db.add(event)
    await db.commit()
    return event
