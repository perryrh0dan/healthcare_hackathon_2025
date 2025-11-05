from typing import TypedDict, List
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, ToolMessage
from .tools import retrieve_context
from .config import logger


class AgentState(TypedDict):
    messages: List[BaseMessage]


class Graph:
    def __init__(self, llm):
        try:
            self.llm = llm.bind_tools([retrieve_context])
            workflow = StateGraph(state_schema=AgentState)
            workflow.add_node("supervisor", self.supervisor_agent)
            workflow.add_edge(START, "supervisor")
            workflow.add_edge("supervisor", END)
            self.graph = workflow.compile()
            logger.info("Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def chat(self, history):
        try:
            logger.debug(f"Invoking graph with {len(history)} messages")
            result = self.graph.invoke({"messages": history})
            ai_response = result["messages"][-1]
            logger.debug("Graph invocation successful")
            return ai_response.content
        except Exception as e:
            logger.error(f"Error during graph chat: {e}")
            return "An error occurred while processing your request."

    def supervisor_agent(self, state: AgentState):
        response = self.llm.invoke(state["messages"])
        messages = state["messages"] + [response]
        while hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                args = tool_call["args"]
                result = retrieve_context.run(args)
                logger.debug(f"Tool result: {result}")
                tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_call["name"])
                messages.append(tool_message)
            response = self.llm.invoke(messages)
            messages = messages + [response]
        return {"messages": messages}
