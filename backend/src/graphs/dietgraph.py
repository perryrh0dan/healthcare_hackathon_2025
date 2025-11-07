from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from ..tools import retrieve_context, add_meal_to_calendar, get_meals_for_day, edit_meal, remove_meal
from ..config import logger


class AgentState(TypedDict):
    messages: List[BaseMessage]
    daily_answers: List[Dict[str, Any]]
    registration_answers: List[Dict[str, str]]
    diet_plan: Dict[str, Any]


from .graph import BaseGraph


def convert_messages_to_langchain(messages: List[Any]) -> List[BaseMessage]:
    converted = []
    for msg in messages:
        if isinstance(msg, BaseMessage):
            converted.append(msg)
        elif hasattr(msg, "role") and hasattr(msg, "content"):
            if msg.role == "user":
                converted.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                converted.append(AIMessage(content=msg.content))
            else:
                converted.append(HumanMessage(content=msg.content))
        else:
            converted.append(HumanMessage(content=str(msg)))
    return converted


class DietGraph(BaseGraph):
    def __init__(self, llm):
        try:
            self.tools = {
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
            logger.info("DietGraph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DietGraph: {e}")
            raise

    def chat(self, history, daily_answers=None, registration_answers=None, diet_plan=None):
        try:
            if daily_answers is None:
                daily_answers = []
            if registration_answers is None:
                registration_answers = []
            if diet_plan is None:
                diet_plan = {}
            # Convert history to LangChain message format
            langchain_history = convert_messages_to_langchain(history)
            logger.debug(f"Invoking DietGraph with {len(langchain_history)} messages")
            result = self.graph.invoke(
                {
                    "messages": langchain_history,
                    "daily_answers": daily_answers,
                    "registration_answers": registration_answers,
                    "diet_plan": diet_plan,
                }
            )
            ai_response = result["messages"][-1]
            logger.debug("DietGraph invocation successful")
            if isinstance(ai_response, dict):
                return ai_response.get("content", str(ai_response))
            else:
                return ai_response.content
        except Exception as e:
            logger.error(f"Error during DietGraph chat: {e}")
            return "An error occurred while processing your diet planning request."

    def supervisor_agent(self, state: AgentState):
        context_msg = f"User's daily answers: {state['daily_answers']}. Registration info: {state['registration_answers']}. Current diet plan: {state['diet_plan']}."
        system_message = SystemMessage(
            content=context_msg
            + " You are a diet planning assistant. Help the user plan their meals for the next days or specific days based on their health information and goals. Avoid any meals that the user does not like. Keep going until you planned all the days you need to plan"
        )
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
