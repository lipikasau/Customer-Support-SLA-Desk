from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, teams, sla_policies, tickets, escalations, reports

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(sla_policies.router, prefix="/sla-policies", tags=["sla-policies"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(escalations.router, prefix="/escalations", tags=["escalations"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
