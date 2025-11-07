from fastapi import APIRouter
from ..state import daily_questions, users, questions_graph
from ..utils import get_recent_messages
from ..config import logger

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/")
def get_daily_questions(user_id: str):
    logger.info(f"Daily questions requested for user: {user_id}")
    base_questions = [
        {"question": "How are you?", "type": "scale", "from": 1, "to": 5},
        {"question": "What is your blood pressure?", "type": "text"},
        {"question": "What is your weight?", "type": "text"},
        {
            "question": "Did you take any medication today?",
            "type": "enum",
            "options": [
                {"label": "Yes", "value": "yes"},
                {"label": "No", "value": "no"},
            ],
        },
    ]
    if user_id not in users:
        logger.warning(f"User {user_id} not found, returning base questions")
        return base_questions
    registration_answers = users[user_id]
    recent_messages = get_recent_messages(user_id)
    additional_questions = questions_graph.chat(recent_messages, registration_answers, base_questions)
    additional_questions = additional_questions[:2]
    return base_questions + additional_questions


@router.post("/")
def submit_daily_answers(answers: list[dict], user_id: str):
    daily_questions[user_id] = answers
    logger.info(f"Received daily answers for user {user_id}: {answers}")
    return {"status": "success"}
