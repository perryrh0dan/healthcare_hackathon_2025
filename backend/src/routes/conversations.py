from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus
from typing import List
from datetime import datetime
from pydantic import BaseModel
from ..db import get_user_conversations, get_conversation, Conversation
from ..config import logger


class ConversationSummary(BaseModel):
    id: str
    title: str | None
    date: datetime


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def get_conversations(request: Request) -> List[ConversationSummary]:
    logger.debug("get_conversations")
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    conversations_dict = get_user_conversations(username)
    conversations = list(conversations_dict.values())

    # Sort by the timestamp of the last message in each conversation
    conversations.sort(
        key=lambda conv: conv.messages[-1].timestamp if conv.messages else datetime.min,
        reverse=True
    )

    # Return only id, title, and date
    return [
        ConversationSummary(
            id=conv.id,
            title=conv.title,
            date=conv.messages[-1].timestamp if conv.messages else datetime.min
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}")
async def get_conversation_by_id(conversation_id: str, request: Request) -> Conversation:
    logger.debug(f"get_conversation_by_id: {conversation_id}")
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    conversation = get_conversation(username, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Conversation not found")

    return conversation