import asyncio
from app.database import async_session_maker
from app.crud.users import user as crud_user
from app.schemas.users import UserCreate
from app.crud.teams import team as crud_team
from app.schemas.teams import TeamCreate
from app.crud.tickets import ticket as crud_ticket
from app.schemas.tickets import TicketCreate

async def setup():
    async with async_session_maker() as db:
        # Create user
        user_in = UserCreate(email="admin@example.com", password="password", full_name="Admin User", is_active=True, is_superuser=True)
        user_db = await crud_user.get_by_email(db, email=user_in.email)
        if not user_db:
            user_db = await crud_user.create(db, obj_in=user_in)
        
        # Create team
        team_in = TeamCreate(name="Support Team", description="Tier 1 Support")
        team_db = await crud_team.get_by_name(db, name=team_in.name)
        if not team_db:
            team_db = await crud_team.create(db, obj_in=team_in)
            
        # Create a dummy ticket
        tickets = await crud_ticket.get_multi(db)
        if not tickets:
            ticket_in = TicketCreate(title="Login not working", description="I can't log in to the portal.", priority="high", status="open", team_id=team_db.id, customer_email="customer@example.com")
            await crud_ticket.create(db, obj_in=ticket_in)

if __name__ == "__main__":
    asyncio.run(setup())
    print("Database seeded!")
