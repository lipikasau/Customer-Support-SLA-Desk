from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List

from app.api.deps import DbSession, CurrentUser
from app.crud.teams import get_teams, get_team, create_team, add_user_to_team
from app.schemas.teams import TeamCreate, TeamResponse, TeamMemberAdd
from app.crud.users import get_user
from app.api.deps import get_current_active_admin

router = APIRouter()

@router.post("/", response_model=TeamResponse)
async def create_new_team(
    team_in: TeamCreate,
    db: DbSession,
    current_user: CurrentUser # Any user can create a team for now, or you can restrict to admin
):
    team = await create_team(db, team_in)
    return team

@router.get("/", response_model=List[TeamResponse])
async def read_teams(
    db: DbSession,
    current_user: CurrentUser
):
    teams = await get_teams(db)
    return teams

@router.post("/{team_id}/members", response_model=dict)
async def add_member_to_team(
    team_id: UUID,
    member_in: TeamMemberAdd,
    db: DbSession,
    current_user: CurrentUser
):
    team = await get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    user = await get_user(db, user_id=member_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await add_user_to_team(db, team_id=team.id, user_id=user.id)
    return {"message": "User added to team successfully"}
