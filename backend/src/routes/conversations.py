from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from typing import List
from datetime import datetime
from pydantic import BaseModel
from ..db import get_user_conversations, get_conversation, Conversation, User
from ..config import logger
from ..utils import get_current_user


class ConversationSummary(BaseModel):
    id: str
    title: str | None
    date: datetime


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def get_conversations(user: User = Depends(get_current_user)) -> List[ConversationSummary]:
    logger.debug("get_conversations")

    conversations_dict = get_user_conversations(user.username)
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
async def get_conversation_by_id(conversation_id: str, user: User = Depends(get_current_user)) -> Conversation:
    logger.debug(f"get_conversation_by_id: {conversation_id}")

    conversation = get_conversation(user.username, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Conversation not found")

    return conversation