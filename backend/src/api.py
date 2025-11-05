from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from typing import Dict, Any
from uuid import uuid4
from .llm import LLM
from .graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from .config import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations: Dict[str, Dict[str, Any]] = {}

try:
    llm = LLM()
    graph = Graph(llm.llm)
    logger.info("API components initialized")
except Exception as e:
    logger.error(f"Failed to initialize API components: {e}")
    raise


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type")

            if msg_type == "ping":
                continue

            message = data.get("message")
            conversation_id = data.get("conversation_id", "")

            if not message:
                logger.warning("Received empty message")
                await websocket.send_json({"error": "No message provided"})
                continue

            if not conversation_id:
                conversation_id = str(uuid4())
                logger.info(f"New conversation started: {conversation_id}")

            conv_data = conversations.get(conversation_id, {"messages": [], "state": {}})
            history = conv_data["messages"]

            history.append({"role": "user", "content": message})

            try:
                messages = [HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) for msg in history]
                response = graph.chat(history=messages)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({"error": "Internal server error"})
                continue

            response_text = response.get("response", response) if isinstance(response, dict) else response

            if response_text:
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text,
                }
                history.append(assistant_msg)
                logger.debug(f"Assistant response sent for conversation {conversation_id}")

            conversations[conversation_id] = {"messages": history}

            await websocket.send_json({"history": history, "conversation_id": conversation_id})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
