from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from src.clients.llm import LLM
from src.graphs.dashboardgraph import DashboardGraph
from src.db import get_daily_dashboard_widgets, User
from ..utils import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/widgets")
async def get_widgets(user: User = Depends(get_current_user)):
    # Try to get pre-generated widgets first
    pre_generated = get_daily_dashboard_widgets(user.username)
    if pre_generated:
        return pre_generated

    # Fallback: generate on-the-fly
    llm = LLM()
    graph = DashboardGraph(llm.llm)
    widgets = graph.run(user.__dict__)
    return widgets

