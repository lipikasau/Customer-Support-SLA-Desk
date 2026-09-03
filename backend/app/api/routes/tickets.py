from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List

from app.api.deps import DbSession, CurrentUser
from app.crud.tickets import get_tickets, get_ticket, create_ticket, update_ticket, add_ticket_comment
from app.schemas.tickets import TicketCreate, TicketUpdate, TicketResponse, TicketCommentCreate, TicketCommentResponse

router = APIRouter()

@router.post("/", response_model=TicketResponse)
async def create_new_ticket(
    ticket_in: TicketCreate,
    db: DbSession,
    current_user: CurrentUser
):
    # Depending on auth, users can only create tickets for themselves, 
    # but agents can create tickets on behalf of customers. 
    # For now, let's just use current_user.id
    try:
        ticket = await create_ticket(db, ticket_in, customer_id=current_user.id)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TicketResponse])
async def read_tickets(
    db: DbSession,
    current_user: CurrentUser
):
    tickets = await get_tickets(db)
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
async def read_ticket(
    ticket_id: UUID,
    db: DbSession,
    current_user: CurrentUser
):
    ticket = await get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_existing_ticket(
    ticket_id: UUID,
    ticket_in: TicketUpdate,
    db: DbSession,
    current_user: CurrentUser
):
    ticket = await get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permissions...
    ticket = await update_ticket(db, ticket, ticket_in, actor_id=current_user.id)
    return ticket

@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def create_ticket_comment(
    ticket_id: UUID,
    comment_in: TicketCommentCreate,
    db: DbSession,
    current_user: CurrentUser
):
    ticket = await get_ticket(db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    comment = await add_ticket_comment(db, ticket, comment_in, author=current_user)
    return comment
