import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta
from .llm import LLM
from .graph import Graph
from .questionsgraph import QuestionsGraph
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

conversations: Dict[str, Dict[str, Dict[str, Any]]] = {
    "test_user": {
        "conv1": {
            "messages": [
                {"role": "user", "content": "I feel tired today", "timestamp": datetime.now()},
                {"role": "assistant", "content": "That sounds concerning. Have you been sleeping well?", "timestamp": datetime.now()},
            ],
            "state": {}
        }
    }
}
daily_questions: Dict[str, list[Dict[str, str]]] = {}
users: Dict[str, list[Dict[str, str]]] = {
    "test_user": [
        {"question": "What is your name?", "answer": "John Doe"},
        {"question": "What is your age?", "answer": "30"},
        {"question": "What is your height?", "answer": "180 cm"},
        {"question": "What is your gender?", "answer": "male"},
        {"question": "Do you have typical health issues. If so what are those?", "answer": "None"},
        {"question": "What is your goal?", "answer": "Stay healthy"},
    ]
}


def get_recent_messages(user_id: str):
    if user_id not in conversations:
        return []
    all_messages = []
    for conv in conversations[user_id].values():
        all_messages.extend(conv["messages"])
    now = datetime.now()
    recent = [msg for msg in all_messages if msg.get("timestamp") and now - msg["timestamp"] < timedelta(hours=24)]
    return recent


try:
    llm = LLM()
    graph = Graph(llm.llm)
    questions_graph = QuestionsGraph(llm.llm)
    logger.info("API components initialized")
except Exception as e:
    logger.error(f"Failed to initialize API components: {e}")
    raise


@app.get("/daily")
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


@app.get("/registration")
def get_registration_questions():
    logger.info("Registration questions requested")
    return [
        {"question": "What is your name?", "type": "text"},
        {"question": "What is your age?", "type": "text"},
        {"question": "What is your height?", "type": "text"},
        {
            "question": "What is your gender?",
            "type": "enum",
            "options": [
                {"label": "Male", "value": "male"},
                {"label": "Female", "value": "female"},
                {"label": "Other", "value": "other"},
            ],
        },
        {"question": "Do you have typical health issues. If so what are those?", "type": "text"},
        {"question": "What is your goal?", "type": "text"},
    ]


@app.post("/daily")
def submit_daily_answers(answers: list[dict], user_id: str):
    daily_questions[user_id] = answers
    logger.info(f"Received daily answers for user {user_id}: {answers}")
    return {"status": "success"}


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
                logger.info(f"New conversation started for user {user_id}: {conversation_id}")

            user_conversations = conversations.setdefault(user_id, {})
            conv_data = user_conversations.get(conversation_id, {"messages": [], "state": {}})
            history = conv_data["messages"]

            history.append({"role": "user", "content": message, "timestamp": datetime.now()})

            try:
                messages = [
                    HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) for msg in history
                ]
                response = graph.chat(messages)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({"error": "Internal server error"})
                continue

            response_text = response.get("response", response) if isinstance(response, dict) else response

            if response_text:
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now(),
                }
                history.append(assistant_msg)
                logger.debug(f"Assistant response sent for user {user_id}, conversation {conversation_id}")

            user_conversations[conversation_id] = {"messages": history}

            await websocket.send_json({"history": history, "conversation_id": conversation_id})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
