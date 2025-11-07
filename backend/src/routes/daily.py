from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Request

from src.db import get_user
from ..state import daily_questions, questions_graph
from ..utils import get_recent_messages
from ..config import logger

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/")
def get_daily_questions(request: Request):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    logger.info(f"Daily questions requested for user: {username}")
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

    recent_messages = get_recent_messages(username)

    additional_questions = questions_graph.chat(recent_messages, base_questions, user)
    additional_questions = additional_questions[:2]
    return base_questions + additional_questions


@router.post("/")
def submit_daily_answers(answers: list[dict], user_id: str):
    daily_questions[user_id] = answers
    logger.info(f"Received daily answers for user {user_id}: {answers}")
    return {"status": "success"}
