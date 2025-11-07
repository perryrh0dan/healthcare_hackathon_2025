from typing import Any, TypedDict, List, Optional
import json
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.db import User
from ..config import logger
from .graph import BaseGraph


class QuestionOption(BaseModel):
    label: str
    value: str


class Question(BaseModel):
    question: str
    type: str
    from_: Optional[int] = Field(None, alias="from")
    to: Optional[int] = None
    options: Optional[List[QuestionOption]] = None


class QuestionList(BaseModel):
    questions: List[Question]


class AgentState(TypedDict):
    user: User
    messages: List[BaseMessage]
    base_questions: list[Any]


class QuestionsGraph(BaseGraph):
    def __init__(self, llm):
        try:
            self.llm = llm
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("supervisor", self.supervisor_agent)
            workflow.add_edge(START, "supervisor")
            workflow.add_edge("supervisor", END)
            self.graph = workflow.compile()
            logger.info("Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def chat(self, history, base_questions, user):
        try:
            logger.debug(f"Invoking graph with {len(history)} messages")
            result = self.graph.invoke(
                {
                    "user": user,
                    "messages": history,
                    "base_questions": base_questions,
                }
            )
            ai_response = result["messages"][-1]
            logger.debug("Graph invocation successful")
            return json.loads(ai_response.content)
        except Exception as e:
            logger.error(f"Error during graph chat: {e}")
            return []



    def supervisor_agent(self, state: AgentState):
        base_questions = state["base_questions"]
        recent_health_summary = state["user"].epa_summary
        question_prompt = f"""Base questions already asked: {base_questions}

Recent health summary: {recent_health_summary}

Generate up to 2 additional daily health questions if needed, different from the base ones."""
        structured_llm = self.llm.with_structured_output(QuestionList)
        response = structured_llm.invoke([HumanMessage(content=question_prompt)])

        state["messages"].append(
            AIMessage(
                content=json.dumps([q.dict(by_alias=True) for q in response.questions])
            )
        )
        return state
