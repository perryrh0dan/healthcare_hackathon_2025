from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime
from .state import graph, summarization_graph
from .routes import documents, user, calendar, daily, diet, dashboard
from .db import (
    create_conversation,
    get_conversation,
    update_conversation,
    get_user,
    Message,
    Conversation,
)
from langchain_core.messages import HumanMessage, AIMessage
from .config import logger

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(user.router)
app.include_router(calendar.router)
app.include_router(daily.router)
app.include_router(diet.router)
app.include_router(dashboard.router)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


@app.post("/chat")
async def chat_endpoint(request: Request, data: ChatRequest, background_tasks: BackgroundTasks):
    user_id = request.cookies.get("user")
    if user_id is None:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    user = get_user(user_id)
    if user is None:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    message = data.message
    conversation_id = data.conversation_id or ""

    if not message:
        logger.warning("Received empty message")
        return {"error": "No message provided"}

    if not conversation_id:
        conversation_id = str(uuid4())
        create_conversation(user_id, conversation_id)
        logger.info(f"New conversation started for user {user_id}: {conversation_id}")

    conv = get_conversation(user_id, conversation_id)
    if conv is None:
        create_conversation(user_id, conversation_id)
        conv = get_conversation(user_id, conversation_id)
    if conv is None:
        conv = Conversation(id=conversation_id)
    history = conv.messages

    history.append(Message(role="user", content=message, timestamp=datetime.now()))

    try:
        messages = [HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content) for msg in history]
        logger.debug(f"Passing context for user {user_id}")
        response = graph.chat(messages, user)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {"error": "Internal server error"}

    response_text = response.get("response", response) if isinstance(response, dict) else response

    if response_text:
        assistant_msg = Message(
            role="assistant",
            content=response_text,
            timestamp=datetime.now(),
        )
        history.append(assistant_msg)
        logger.debug(f"Assistant response sent for user {user_id}, conversation {conversation_id}")

    update_conversation(user_id, conversation_id, history, conv.state)

    # Trigger async summarization
    messages_for_summary = [HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content) for msg in history]
    background_tasks.add_task(summarization_graph.chat, messages_for_summary, user)

    # Convert messages to JSON-serializable format
    history_serializable = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in history
    ]

    return {"history": history_serializable, "conversation_id": conversation_id}
