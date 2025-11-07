from abc import ABC
from typing import TypedDict, List, Dict, Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from ..config import logger
import json


class Widget(BaseModel):
    title: str
    type: Literal["text"] = "text"
    body: str = Field(..., max_length=30)


class WidgetResponse(BaseModel):
    widgets: List[Widget]


class AgentState(TypedDict):
    user_data: Dict
    widgets: List[Widget]


class DashboardGraph(ABC):
    def __init__(self, llm):
        try:
            self.llm = llm
            self.structured_llm = self.llm.with_structured_output(WidgetResponse)
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("widget_generator", self.widget_agent)
            workflow.add_edge(START, "widget_generator")
            workflow.add_edge("widget_generator", END)
            self.graph = workflow.compile()
            logger.info("DashboardGraph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DashboardGraph: {e}")
            raise

    def run(self, user_data: Dict) -> List[Widget]:
        try:
            logger.debug(f"Invoking DashboardGraph with user data for {user_data.get('username', 'unknown')}")
            result = self.graph.invoke(
                {
                    "user_data": user_data,
                    "widgets": [],
                }
            )
            widgets = result["widgets"]
            logger.debug("DashboardGraph invocation successful")
            return widgets
        except Exception as e:
            logger.error(f"Error during DashboardGraph run: {e}")
            return []

    def widget_agent(self, state: AgentState):
        user_data = state["user_data"]
        messages = [
            SystemMessage(
                content=f"""[Role]
You are a health dashboard assistant. Based on the user's profile data, generate exactly 4 personalized widgets with useful short insights for their health dashboard.

Each widget has title, type (always "text"), and body (max 30 characters).

Focus on:
1. Health overview summary
2. Current goals and progress
3. Important reminders or alerts (e.g., allergies, issues)
4. Personalized health stats or ongoing tips

Provide concise, actionable insights. Type must always be "text". Keep body under 30 characters.

[User Data]
{json.dumps(user_data)}
"""
            ),
        ]

        try:
            response = self.structured_llm.invoke(messages)
            state["widgets"] = response.widgets
        except Exception as e:
            logger.error(f"Failed to generate structured widgets: {e}")
            # Fallback to default widgets
            state["widgets"] = [
                Widget(title="Health Overview", body="Generation failed."),
                Widget(title="Goals", body="Generation failed."),
                Widget(title="Reminders", body="Generation failed."),
                Widget(title="Stats", body="Generation failed."),
            ]
        return state