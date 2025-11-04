from typing import TypedDict, List
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, ToolMessage
from .tools import retrieve_context


class AgentState(TypedDict):
    messages: List[BaseMessage]


class Graph:
    def __init__(self, llm):
        self.llm = llm.bind_tools([retrieve_context])
        workflow = StateGraph(state_schema=AgentState)
        workflow.add_node("supervisor", self.supervisor_agent)
        workflow.add_edge(START, "supervisor")
        workflow.add_edge("supervisor", END)
        self.graph = workflow.compile()

    def chat(self, history):
        result = self.graph.invoke({"messages": history})
        ai_response = result["messages"][-1]

        return ai_response.content

    def supervisor_agent(self, state: AgentState):
        response = self.llm.invoke(state["messages"])
        messages = state["messages"] + [response]
        while hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                args = tool_call["args"]
                result = retrieve_context.run(args)
                print(f"Tool result {result}")
                tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_call["name"])
                messages.append(tool_message)
            response = self.llm.invoke(messages)
            messages = state["messages"] + [response]
        return {"messages": messages}
