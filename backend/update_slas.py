import asyncio
from app.database import async_session_maker
from app.models import SLAPolicy, PriorityEnum
from sqlalchemy import select, delete

async def update_policies():
    async with async_session_maker() as db:
        # Get existing policies
        policies = (await db.execute(select(SLAPolicy))).scalars().all()
        
        # We can just update the names of the existing ones if we want, or clear and recreate.
        # But tickets might reference them. Let's update existing names and add missing ones.
        
        policy_map = {p.name: p for p in policies}
        
        # Update existing
        for p in policies:
            if p.name == "Standard SLA":
                p.name = "Standard (24h)"
            elif p.name == "Urgent SLA":
                p.name = "Urgent (4h)"
                
        # Check if Priority (8h) and Critical (1h) exist
        if not any(p.name == "Priority (8h)" for p in policies):
            p_priority = SLAPolicy(
                name="Priority (8h)",
                priority=PriorityEnum.high,
                first_response_minutes=60,
                resolution_minutes=480,
                business_hours_only=True
            )
            db.add(p_priority)
            
        if not any(p.name == "Critical (1h)" for p in policies):
            p_critical = SLAPolicy(
                name="Critical (1h)",
                priority=PriorityEnum.urgent,
                first_response_minutes=15,
                resolution_minutes=60,
                business_hours_only=False
            )
            db.add(p_critical)
            
        await db.commit()
        print("SLA policies updated successfully")

if __name__ == "__main__":
    asyncio.run(update_policies())
