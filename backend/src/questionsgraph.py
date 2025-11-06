from typing import Any, TypedDict, List, Optional
import json
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from .config import logger
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict


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
    messages: List[BaseMessage]
    summarization: str
    registration_answers: list[Dict[str, str]]
    base_questions: list[Any]


class QuestionsGraph:
    def __init__(self, llm):
        try:
            self.llm = llm
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("summarizer", self.summarization_agent)
            workflow.add_node("supervisor", self.supervisor_agent)
            workflow.add_edge(START, "summarizer")
            workflow.add_edge("summarizer", "supervisor")
            workflow.add_edge("supervisor", END)
            self.graph = workflow.compile()
            logger.info("Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def chat(self, history, registration_answers, base_questions):
        try:
            logger.debug(f"Invoking graph with {len(history)} messages")
            result = self.graph.invoke(
                {"messages": history, "registration_answers": registration_answers, "base_questions": base_questions, "summarization": ""}
            )
            ai_response = result["messages"][-1]
            logger.debug("Graph invocation successful")
            return json.loads(ai_response.content)
        except Exception as e:
            logger.error(f"Error during graph chat: {e}")
            return []

    def summarization_agent(self, state: AgentState):
        history = [
            SystemMessage(content="Summarize the previous conversation:"),
            HumanMessage(content="\n".join([str(msg) for msg in state["messages"]])),
        ]

        summary_response = self.llm.invoke(history)
        summary_msg = f"Conversation Summary: {summary_response.content}"
        state["summarization"] = summary_msg
        return state

    def supervisor_agent(self, state: AgentState):
        base_questions = state["base_questions"]
        registration_answers = state["registration_answers"]
        health_summary = state["summarization"]
        question_prompt = f"""Based on user registration answers: {registration_answers}
Base questions already asked: {base_questions}
Health summary: {health_summary}
Generate up to 2 additional daily health questions if needed, different from the base ones."""
        structured_llm = self.llm.with_structured_output(QuestionList)
        response = structured_llm.invoke([HumanMessage(content=question_prompt)])

        state["messages"].append(AIMessage(content=json.dumps([q.dict(by_alias=True) for q in response.questions])))
        return state
