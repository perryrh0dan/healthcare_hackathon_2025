from fastapi import APIRouter, Depends
from ..state import diet_graph
from ..utils import get_recent_messages, get_current_user
from ..config import logger
from typing import Dict, Any, Optional, TypedDict
from src.db import get_daily_answers, User


class DietPlanDTO(TypedDict):
    days: int
    preferences: Optional[Dict[str, Any]]


router = APIRouter(prefix="/diet", tags=["diet"])


@router.post("/plan")
def plan_diet(data: DietPlanDTO, user: User = Depends(get_current_user)):
    days = data["days"]
    preferences = data.get("preferences")
    logger.info(f"Diet planning requested for user: {user.username}, days: {days}")

    registration_answers = user.__dict__
    daily_answers_history = get_daily_answers(user.username)
    latest_answers = daily_answers_history[-1].answers if daily_answers_history else []
    recent_messages = get_recent_messages(user.username)

    diet_prompt = f"Plan a {days}-day diet based on the user's health information and preferences: {preferences or {}}"

    from langchain_core.messages import HumanMessage

    messages = recent_messages + [HumanMessage(content=diet_prompt)]

    diet_plan = diet_graph.chat(messages, latest_answers, registration_answers)

    return {"diet_plan": diet_plan}
