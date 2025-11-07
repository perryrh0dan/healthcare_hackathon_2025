from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus
from src.clients.llm import LLM
from src.graphs.dashboardgraph import DashboardGraph
from src.db import get_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/widgets")
async def get_widgets(request: Request):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    llm = LLM()
    graph = DashboardGraph(llm.llm)
    widgets = graph.run(user.__dict__)
    return widgets