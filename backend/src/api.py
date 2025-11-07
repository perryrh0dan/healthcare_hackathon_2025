from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks, Request, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime
import base64
import os
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
    image: Optional[UploadFile] = None


@app.post("/chat")
async def chat_endpoint(background_tasks: BackgroundTasks, request: Request, message: str = Form(...), conversation_id: Optional[str] = Form(None), image: Optional[UploadFile] = Form(None)):
    user_id = request.cookies.get("user")
    if user_id is None:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    user = get_user(user_id)
    if user is None:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}

    conversation_id = conversation_id or ""

    if not message and not image:
        logger.warning("Received empty message and no image")
        return {"error": "No message or image provided"}

    image_path = None
    if image:
        image_content = await image.read()
        # Generate unique filename
        if image.filename and '.' in image.filename:
            ext = image.filename.split('.')[-1]
        else:
            ext = 'jpg'
        filename = f"{uuid4()}.{ext}"
        image_path = f"uploads/{filename}"
        with open(image_path, "wb") as f:
            f.write(image_content)

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

    history.append(Message(role="user", content=message, timestamp=datetime.now(), image=image_path))

    messages = []
    for msg in history:
        if msg.role == "user":
            if msg.image:
                with open(msg.image, "rb") as f:
                    image_content = f.read()
                image_url = f"data:image/jpeg;base64,{base64.b64encode(image_content).decode('utf-8')}"
                content = [{"type": "text", "text": msg.content}, {"type": "image_url", "image_url": {"url": image_url}}]
            else:
                content = msg.content
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=msg.content))

    try:
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
            "image": msg.image,
        }
        for msg in history
    ]

    return {"history": history_serializable, "conversation_id": conversation_id}


@app.get("/images/{path:path}")
async def get_image(path: str):
    if not os.path.exists(path):
        return {"error": "Image not found"}
    return FileResponse(path, media_type='image/jpeg')
