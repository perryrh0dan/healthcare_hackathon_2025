from fastapi import APIRouter, Depends
from ..state import diet_graph
from ..utils import get_recent_messages, get_current_user
from ..config import logger
from typing import Dict, Any, Optional, TypedDict
from src.db import get_daily_answers, User


class DietPlanDTO(TypedDict):
    days: int
    start_date: Optional[str]
    preferences: Optional[Dict[str, Any]]


router = APIRouter(prefix="/diet", tags=["diet"])


@router.post("/plan")
def plan_diet(data: DietPlanDTO, user: User = Depends(get_current_user)):
    days = data["days"]
    start_date = data.get("start_date")
    preferences = data.get("preferences")
    logger.info(f"Diet planning requested for user: {user.username}, days: {days}, start_date: {start_date}")

    registration_answers = user.__dict__
    daily_answers_history = get_daily_answers(user.username)
    latest_answers = daily_answers_history[-1].answers if daily_answers_history else []
    recent_messages = get_recent_messages(user.username)

    diet_prompt = f"Plan a {days}-day diet starting from {start_date} based on the user's health information and preferences: {preferences or {}}. Ensure you create meals for ALL {days} days."

    from langchain_core.messages import HumanMessage

    messages = recent_messages + [HumanMessage(content=diet_prompt)]

    diet_plan_state = {"days": days, "start_date": start_date}
    diet_plan = diet_graph.chat(messages, latest_answers, registration_answers, diet_plan_state)

    return {"diet_plan": diet_plan}
