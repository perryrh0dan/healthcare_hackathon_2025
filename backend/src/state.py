from typing import Dict
from .clients.llm import LLM
from .graphs.chatgraph import ChatGraph
from .graphs.questionsgraph import QuestionsGraph
from .config import logger

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


try:
    llm = LLM()
    graph = ChatGraph(llm.llm)
    questions_graph = QuestionsGraph(llm.llm)
    logger.info("API components initialized")
except Exception as e:
    logger.error(f"Failed to initialize API components: {e}")
    raise
