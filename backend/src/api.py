from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from uuid import uuid4
from datetime import datetime
from .state import graph
from .routes import documents, user, calendar, daily, diet, dashboard
from .db import (
    create_conversation,
    get_conversation,
    update_conversation,
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


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type")

            if msg_type == "ping":
                continue

            user_id = data.get("user_id")
            if not user_id:
                logger.warning("No user_id provided in WebSocket message")
                await websocket.send_json({"error": "user_id required"})
                continue

            message = data.get("message")
            conversation_id = data.get("conversation_id", "")

            if not message:
                logger.warning("Received empty message")
                await websocket.send_json({"error": "No message provided"})
                continue

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
                await websocket.send_json({"error": "Internal server error"})
                continue

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

            # Convert messages to JSON-serializable format
            history_serializable = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in history
            ]

            await websocket.send_json({"history": history_serializable, "conversation_id": conversation_id})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
