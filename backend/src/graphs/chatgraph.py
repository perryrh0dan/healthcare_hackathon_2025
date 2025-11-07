from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from ..tools import (
    retrieve_context,
    get_calendar,
    add_calendar_event,
    remove_calendar_event,
    edit_calendar_event,
    add_meal_to_calendar,
    get_meals_for_day,
    edit_meal,
    remove_meal,
)
from ..config import logger


class AgentState(TypedDict):
    messages: List[BaseMessage]
    daily_answers: List[Dict[str, Any]]
    registration_answers: List[Dict[str, str]]


from .graph import BaseGraph


class ChatGraph(BaseGraph):
    def __init__(self, llm):
        try:
            self.tools = {
                "retrieve_context": retrieve_context,
                "get_calendar": get_calendar,
                "add_calendar_event": add_calendar_event,
                "remove_calendar_event": remove_calendar_event,
                "edit_calendar_event": edit_calendar_event,
                "add_meal_to_calendar": add_meal_to_calendar,
                "get_meals_for_day": get_meals_for_day,
                "edit_meal": edit_meal,
                "remove_meal": remove_meal,
            }
            self.llm = llm.bind_tools(list(self.tools.values()))
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("supervisor", self.supervisor_agent)
            workflow.add_edge(START, "supervisor")
            workflow.add_edge("supervisor", END)
            self.graph = workflow.compile()
            logger.info("Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def chat(self, history, daily_answers=None, registration_answers=None):
        try:
            if daily_answers is None:
                daily_answers = []
            if registration_answers is None:
                registration_answers = []
            logger.debug(f"Invoking graph with {len(history)} messages")
            result = self.graph.invoke({"messages": history, "daily_answers": daily_answers, "registration_answers": registration_answers})
            ai_response = result["messages"][-1]
            logger.debug("Graph invocation successful")
            if isinstance(ai_response, dict):
                return ai_response.get("content", str(ai_response))
            else:
                return ai_response.content
        except Exception as e:
            logger.error(f"Error during graph chat: {e}")
            return "An error occurred while processing your request."

    def supervisor_agent(self, state: AgentState):
        context_msg = f"You are a healthcare agent inside a product from 316er studios. You get user messages and potentially images. Try to match the tone of the user. If the user is scarred because of a illness try to support him. If he needs to go to the doctor try to motivate him. Try to identify potentiall health issues early on. Add events to the calendar if needed. Replan the users diet on request. Be a proactive agent. User's daily answers: {state['daily_answers']}. Registration info: {state['registration_answers']}."
        system_message = SystemMessage(content=context_msg)
        messages_with_context = [system_message] + state["messages"]

        response = self.llm.invoke(messages_with_context)
        messages = messages_with_context + [response]
        while hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                args = tool_call["args"]
                logger.debug(f"Executing tool: {tool_name} with args: {args}")

                tool_func = self.tools.get(tool_name)
                if tool_func:
                    result = tool_func.run(args)
                else:
                    result = f"Unknown tool: {tool_name}"

                logger.debug(f"Tool result: {result}")
                tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_call["name"])
                messages.append(tool_message)
            response = self.llm.invoke(messages)
            messages = messages + [response]
        return {"messages": messages}
