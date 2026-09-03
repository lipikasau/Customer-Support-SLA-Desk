import asyncio
from datetime import datetime, timezone, timedelta
from app.database import async_session_maker, engine, Base
from app.models import User, RoleEnum, SLAPolicy, PriorityEnum, Ticket, TicketStatusEnum, Escalation
from app.core.security import get_password_hash
from app.crud.tickets import add_ticket_event
from app.core.sla import add_business_minutes

async def seed_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session_maker() as db:
        # Check if users exist to prevent duplicate seeding
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        if result.scalars().first():
            print("Database already seeded. Aborting.")
            return

        print("Seeding database...")
        
        # 1. Create Users
        password_hash = get_password_hash("password")
        
        admin = User(email="admin@sladesk.com", full_name="Admin User", role=RoleEnum.admin, hashed_password=password_hash)
        manager = User(email="manager@sladesk.com", full_name="Manager User", role=RoleEnum.manager, hashed_password=password_hash)
        agent1 = User(email="agent1@sladesk.com", full_name="Alice (Agent)", role=RoleEnum.agent, hashed_password=password_hash)
        agent2 = User(email="agent2@sladesk.com", full_name="Bob (Agent)", role=RoleEnum.agent, hashed_password=password_hash)
        customer1 = User(email="customer1@gmail.com", full_name="Charlie (Customer)", role=RoleEnum.customer, hashed_password=password_hash)
        customer2 = User(email="customer2@gmail.com", full_name="Diana (Customer)", role=RoleEnum.customer, hashed_password=password_hash)
        
        db.add_all([admin, manager, agent1, agent2, customer1, customer2])
        await db.commit()
        
        # 2. Create SLA Policies
        policy_standard = SLAPolicy(
            name="Standard SLA",
            priority=PriorityEnum.medium,
            first_response_minutes=120, # 2 hours
            resolution_minutes=1440, # 24 business hours
            business_hours_only=True
        )
        policy_urgent = SLAPolicy(
            name="Urgent SLA",
            priority=PriorityEnum.urgent,
            first_response_minutes=15, # 15 mins
            resolution_minutes=240, # 4 business hours
            business_hours_only=True
        )
        db.add_all([policy_standard, policy_urgent])
        await db.commit()
        
        # 3. Create Tickets
        now = datetime.now(timezone.utc)
        
        # Ticket 1: Open, near SLA breach
        t1 = Ticket(
            subject="Help! Cannot access my account",
            description="I've been trying to login all morning but it keeps saying invalid credentials.",
            customer_id=customer1.id,
            priority=PriorityEnum.high,
            status=TicketStatusEnum.open,
            sla_policy_id=policy_urgent.id,
            sla_first_response_due_at=add_business_minutes(now, 5), # Breaching very soon!
            sla_resolution_due_at=add_business_minutes(now, 240),
            created_at=now - timedelta(minutes=10)
        )
        
        # Ticket 2: Breached!
        t2 = Ticket(
            subject="Billing issue on invoice #1024",
            description="I was double charged.",
            customer_id=customer2.id,
            assigned_agent_id=agent1.id,
            priority=PriorityEnum.urgent,
            status=TicketStatusEnum.open,
            sla_policy_id=policy_urgent.id,
            sla_first_response_due_at=now - timedelta(minutes=10), # Breached 10 mins ago
            sla_resolution_due_at=add_business_minutes(now, 240),
            created_at=now - timedelta(minutes=30),
            first_response_breached=True
        )
        
        # Ticket 3: In Progress, healthy
        t3 = Ticket(
            subject="How do I change my profile picture?",
            description="Can't find the setting.",
            customer_id=customer1.id,
            assigned_agent_id=agent2.id,
            priority=PriorityEnum.low,
            status=TicketStatusEnum.in_progress,
            sla_policy_id=policy_standard.id,
            sla_first_response_due_at=add_business_minutes(now - timedelta(minutes=60), 120),
            sla_resolution_due_at=add_business_minutes(now - timedelta(minutes=60), 1440),
            created_at=now - timedelta(minutes=60),
            first_responded_at=now - timedelta(minutes=45)
        )
        
        # Ticket 4: Resolved
        t4 = Ticket(
            subject="System is down",
            description="Is there a maintenance going on?",
            customer_id=customer2.id,
            assigned_agent_id=agent1.id,
            priority=PriorityEnum.urgent,
            status=TicketStatusEnum.resolved,
            sla_policy_id=policy_urgent.id,
            sla_first_response_due_at=now - timedelta(days=2),
            sla_resolution_due_at=now - timedelta(days=1),
            created_at=now - timedelta(days=2, hours=1),
            first_responded_at=now - timedelta(days=2, hours=0, minutes=45),
            resolved_at=now - timedelta(days=2, hours=0, minutes=30)
        )
        
        db.add_all([t1, t2, t3, t4])
        await db.commit()
        
        # Escalation for the breached ticket
        esc1 = Escalation(
            ticket_id=t2.id,
            escalated_to=manager.id,
            reason="first_response_sla_breached",
            created_at=now - timedelta(minutes=5)
        )
        db.add(esc1)
        await db.commit()

        print("Database seeded successfully!")
        print("Test Accounts (password for all is 'password'):")
        print("- manager@sladesk.com")
        print("- agent1@sladesk.com")
        print("- customer1@gmail.com")

if __name__ == "__main__":
    asyncio.run(seed_db())
