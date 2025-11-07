from abc import ABC
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage
from ..config import logger


class AgentState(TypedDict):
    epa: str
    summary: str


class EPAGraph(ABC):
    def __init__(self, llm):
        try:
            self.llm = llm
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("summarizer", self.summary_agent)
            workflow.add_edge(START, "summarizer")
            workflow.add_edge("summarizer", END)
            self.graph = workflow.compile()
            logger.info("Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def run(self, epa):
        try:
            logger.debug(f"Invoking graph with {len(epa)} long ePA")
            result = self.graph.invoke(
                {
                    "epa": epa,
                    "summary": "",
                }
            )
            ai_response = result["summary"]
            logger.debug("Graph invocation successful")
            return ai_response
        except Exception as e:
            logger.error(f"Error during graph chat: {e}")
            return ""

    def summary_agent(self, state: AgentState):
        epa = state["epa"]
        messages = [
            SystemMessage(
                content=f"""[Role]
You are a clinical summary AI assistant. Your task is to read a full electronic patient record (EPR) and generate a comprehensive, accurate, and concise summary containing all important medical information about the patient. The summary should serve as a reliable context source for future interactions or automated reasoning.

[Data]
{epa}
"""
            ),
        ]

        summary_response = self.llm.invoke(messages)
        summary_msg = f"Conversation Summary: {summary_response.content}"
        state["summary"] = summary_msg
        return state
