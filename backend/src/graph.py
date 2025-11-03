from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages: List[Dict[str, str]]


class Graph:
    def __init__(self, llm):
        self.llm = llm
        workflow = StateGraph(state_schema=AgentState)
        workflow.add_node("supervisor", self.supervisor_agent)
        workflow.add_edge("supervisor", END)
        self.graph = workflow.compile()

    def chat(self, history):
        result = self.graph.invoke({"messages": history})
        ai_response = result["messages"][-1]

        return ai_response.content

    def supervisor_agent(self, state: AgentState):
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}
