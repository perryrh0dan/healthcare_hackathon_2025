from fastapi import APIRouter
from ..state import users, diet_graph, daily_questions
from ..utils import get_recent_messages
from ..config import logger
from typing import Dict, Any

router = APIRouter(prefix="/diet", tags=["diet"])


@router.post("/plan")
def plan_diet(user_id: str, days: int = 7, preferences: Dict[str, Any] = None):
    logger.info(f"Diet planning requested for user: {user_id}, days: {days}")
    if user_id not in users:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    registration_answers = users[user_id]
    daily_answers = daily_questions.get(user_id, [])
    recent_messages = get_recent_messages(user_id)

    diet_prompt = f"Plan a {days}-day diet based on the user's health information and preferences: {preferences or {}}"

    from langchain_core.messages import HumanMessage

    messages = recent_messages + [HumanMessage(content=diet_prompt)]

    diet_plan = diet_graph.chat(messages, daily_answers, registration_answers)

    return {"diet_plan": diet_plan}
