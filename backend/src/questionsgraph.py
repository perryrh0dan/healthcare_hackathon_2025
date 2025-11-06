from typing import TypedDict, List
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from .tools import retrieve_context
from .config import logger


class AgentState(TypedDict):
    messages: List[BaseMessage]
    summarization: str


class QuestionsGraph:
    def __init__(self, llm):
        try:
            self.llm = llm  # .bind_tools([retrieve_context])
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

    def summarization_agent(self, state: AgentState):
        history = "\n".join([msg.content for msg in state["messages"]])
        prompt = f"Summarize the previous conversation:\n\n{history}"
        summary_response = self.llm.invoke([HumanMessage(content=prompt)])
        summary_msg = f"Conversation Summary: {summary_response.content}"
        state["summarization"] = summary_msg
        return state

    def supervisor_agent(self, state: AgentState):
        response = self.llm.invoke(state["messages"])
        messages = state["messages"] + [response]
        return {"messages": messages}
