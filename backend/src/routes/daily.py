from http import HTTPStatus
from typing import List, Literal, Optional, TypedDict
from fastapi import APIRouter, HTTPException, Request

from src.db import Answer, get_user, save_daily_answers
from ..state import questions_graph
from ..utils import get_recent_messages
from ..config import logger

router = APIRouter(prefix="/daily", tags=["daily"])


class DailyQuestionOption(TypedDict):
    label: str
    value: str


class DailyQuestion(TypedDict):
    question: str
    type: Literal["text", "number", "enum"]
    options: Optional[list[DailyQuestionOption]]
    optional: bool


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
        DailyQuestion(
            question="How are you?",
            type="enum",
            options=[
                DailyQuestionOption(value="verygood", label="Very good"),
                DailyQuestionOption(value="good", label="Good"),
                DailyQuestionOption(value="okay", label="Okay"),
                DailyQuestionOption(value="notgood", label="Not good"),
                DailyQuestionOption(value="bad", label="Bad"),
            ],
            optional=False,
        ),
        DailyQuestion(
            question="What is your blood pressure?",
            type="text",
            options=None,
            optional=False,
        ),
        DailyQuestion(
            question="What is your weight?",
            type="number",
            options=None,
            optional=False,
        ),
        DailyQuestion(
            question="Did you take any medication today?",
            type="enum",
            options=[
                DailyQuestionOption(value="yes", label="Yes"),
                DailyQuestionOption(value="no", label="No"),
            ],
            optional=False,
        ),
    ]

    recent_messages = get_recent_messages(username)

    additional_questions = questions_graph.chat(recent_messages, base_questions, user)
    additional_questions = additional_questions[:2]
    return base_questions + additional_questions


class AnswerDTO(TypedDict):
    question: str
    answer: str


@router.post("/")
def submit_daily_answers(data: List[AnswerDTO], request: Request):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    answers = [
        Answer(question=answer["question"], answer=answer["answer"]) for answer in data
    ]

    save_daily_answers(username, answers)
    logger.info(f"Received daily answers for user {username}: {answers}")
    return {"status": "success"}
