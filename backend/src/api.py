from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta

from .routes import documents, user, calendar, daily
from .state import graph, users, conversations, daily_questions
from langchain_core.messages import HumanMessage, AIMessage
from .config import logger

app = FastAPI()

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




@app.post("/registration")
def submit_registration_answers(answers: list[Dict[str, str]]):
    user_id = str(uuid4())
    users[user_id] = answers
    logger.info(f"New user registered with ID {user_id}: {answers}")
    return {"user_id": user_id}


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
                logger.info(
                    f"New conversation started for user {user_id}: {conversation_id}"
                )

            user_conversations = conversations.setdefault(user_id, {})
            conv_data = user_conversations.get(
                conversation_id, {"messages": [], "state": {}}
            )
            history = conv_data["messages"]

            history.append(
                {"role": "user", "content": message, "timestamp": datetime.now()}
            )

            try:
                messages = [
                    HumanMessage(content=msg["content"])
                    if msg["role"] == "user"
                    else AIMessage(content=msg["content"])
                    for msg in history
                ]
                daily_answers = daily_questions.get(user_id, [])
                registration_answers = users.get(user_id, [])
                logger.debug(
                    f"Passing context for user {user_id}: daily_answers={len(daily_answers)}, registration_answers={len(registration_answers)}"
                )
                response = graph.chat(messages, daily_answers, registration_answers)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({"error": "Internal server error"})
                continue

            response_text = (
                response.get("response", response)
                if isinstance(response, dict)
                else response
            )

            if response_text:
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now(),
                }
                history.append(assistant_msg)
                logger.debug(
                    f"Assistant response sent for user {user_id}, conversation {conversation_id}"
                )

            user_conversations[conversation_id] = {"messages": history}

            await websocket.send_json(
                {"history": history, "conversation_id": conversation_id}
            )
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
