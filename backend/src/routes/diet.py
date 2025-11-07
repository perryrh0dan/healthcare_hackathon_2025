from fastapi import APIRouter
from ..state import diet_graph
from ..utils import get_recent_messages
from ..config import logger
from typing import Dict, Any
from src.db import get_user, get_daily_answers

router = APIRouter(prefix="/diet", tags=["diet"])


@router.post("/plan")
def plan_diet(user_id: str, days: int = 7, preferences: Dict[str, Any] = None):
    logger.info(f"Diet planning requested for user: {user_id}, days: {days}")
    user = get_user(user_id)
    if user is None:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    registration_answers = user.__dict__
    daily_answers = get_daily_answers(user_id)
    recent_messages = get_recent_messages(user_id)

    diet_prompt = f"Plan a {days}-day diet based on the user's health information and preferences: {preferences or {}}"

    from langchain_core.messages import HumanMessage

    messages = recent_messages + [HumanMessage(content=diet_prompt)]

    diet_plan = diet_graph.chat(messages, daily_answers, registration_answers)

    return {"diet_plan": diet_plan}
