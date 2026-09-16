import asyncio
from app.database import async_session_maker
from app.models import SLAPolicy
from sqlalchemy import select

async def main():
    async with async_session_maker() as db:
        policies = (await db.execute(select(SLAPolicy))).scalars().all()
        for p in policies:
            print(f"ID: {p.id}, NAME: '{p.name}'")

if __name__ == "__main__":
    asyncio.run(main())
