from typing import Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from .clients.llm import LLM
from .graphs.chatgraph import ChatGraph
from .graphs.questionsgraph import QuestionsGraph
from .config import logger

conversations: Dict[str, Dict[str, Dict[str, Any]]] = {
    "test_user": {
        "conv1": {
            "messages": [
                {
                    "role": "user",
                    "content": "I feel tired today",
                    "timestamp": datetime.now(),
                },
                {
                    "role": "assistant",
                    "content": "That sounds concerning. Have you been sleeping well?",
                    "timestamp": datetime.now(),
                },
            ],
            "state": {},
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
        {
            "question": "Do you have typical health issues. If so what are those?",
            "answer": "None",
        },
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
    recent = [
        msg
        for msg in all_messages
        if msg.get("timestamp") and now - msg["timestamp"] < timedelta(hours=24)
    ]
    return recent


try:
    llm = LLM()
    graph = ChatGraph(llm.llm)
    questions_graph = QuestionsGraph(llm.llm)
    logger.info("API components initialized")
except Exception as e:
    logger.error(f"Failed to initialize API components: {e}")
    raise