from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models import Team, User
from app.schemas.teams import TeamCreate

async def create_team(db: AsyncSession, team_in: TeamCreate) -> Team:
    db_team = Team(name=team_in.name)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team

async def get_teams(db: AsyncSession) -> list[Team]:
    result = await db.execute(select(Team))
    return list(result.scalars().all())

async def get_team(db: AsyncSession, team_id: UUID) -> Team | None:
    result = await db.execute(select(Team).where(Team.id == team_id))
    return result.scalars().first()

from sqlalchemy import insert
from app.models import team_members

async def add_user_to_team(db: AsyncSession, team_id: UUID, user_id: UUID) -> None:
    await db.execute(
        insert(team_members).values(team_id=team_id, user_id=user_id)
    )
    await db.commit()

