from typing import List
from langchain_core.messages import BaseMessage, HumanMessage
from src.db import User, update_recent_summary
from ..config import logger
from .graph import BaseGraph


class SummarizationGraph(BaseGraph):
    def __init__(self, llm):
        self.llm = llm

    def chat(self, history: List[BaseMessage], user: User):
        try:
            recent_messages = history[-5:] if len(history) > 5 else history
            prompt = f"Summarize the recent conversation briefly:\n" + "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])
            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary = response.content
            update_recent_summary(user.username, summary)
            logger.info(f"Updated recent summary for user {user.username}")
        except Exception as e:
            logger.error(f"Error summarizing conversation for user {user.username}: {e}")
