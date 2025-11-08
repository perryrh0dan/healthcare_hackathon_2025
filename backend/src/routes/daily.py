from http import HTTPStatus
from typing import List, Literal, Optional, TypedDict
from fastapi import APIRouter, HTTPException, Depends

from src.db import (
    Answer,
    save_daily_answers,
    get_daily_questions as get_stored_daily_questions,
    save_daily_questions,
    User,
)
from ..state import questions_graph
from ..utils import get_recent_messages, get_current_user
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
    field: str


@router.get("/")
def get_daily_questions(user: User = Depends(get_current_user)):
    logger.info(f"Daily questions requested for user: {user.username}")

    # Try to get pre-generated questions first
    pre_generated = get_stored_daily_questions(user.username)
    if pre_generated:
        return pre_generated

    # Fallback: generate on-the-fly
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
            field="mood",
        ),
        DailyQuestion(
            question="What is your blood pressure?",
            type="text",
            options=None,
            optional=False,
            field="blood_pressure",
        ),
        DailyQuestion(
            question="What is your weight?",
            type="number",
            options=None,
            optional=False,
            field="weight",
        ),
        DailyQuestion(
            question="Did you take any medication today?",
            type="enum",
            options=[
                DailyQuestionOption(value="yes", label="Yes"),
                DailyQuestionOption(value="no", label="No"),
            ],
            optional=False,
            field="medication",
        ),
    ]

    recent_messages = get_recent_messages(user.username)

    additional_questions = questions_graph.chat(recent_messages, base_questions, user)
    additional_questions = additional_questions[:2]
    all_questions = base_questions + additional_questions
    save_daily_questions(user.username, all_questions)
    return all_questions


class AnswerDTO(TypedDict):
    question: str
    answer: str
    field: str


@router.post("/")
def submit_daily_answers(data: List[AnswerDTO], user: User = Depends(get_current_user)):
    if not user.needs_daily_questions:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Daily questionnaire already submitted today",
        )

    answers = [
        Answer(
            question=answer["question"], answer=answer["answer"], field=answer["field"]
        )
        for answer in data
    ]

    save_daily_answers(user.username, answers)
    logger.info(f"Received daily answers for user {user.username}: {answers}")
    return {"status": "success"}
