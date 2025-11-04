from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from typing import Dict, Any
from uuid import uuid4
from .llm import LLM
from .graph import Graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations: Dict[str, Dict[str, Any]] = {}

llm = LLM()

graph = Graph(llm.llm)


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
                await websocket.send_json({"error": "No message provided"})
                continue

            if not conversation_id:
                conversation_id = str(uuid4())

            conv_data = conversations.get(conversation_id, {"messages": [], "state": {}})
            history = conv_data["messages"]

            history.append({"role": "user", "content": message})

            response = graph.chat(history=history)

            response_text = response.get("response", response) if isinstance(response, dict) else response

            if response_text:
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text,
                }
                history.append(assistant_msg)

            conversations[conversation_id] = {"messages": history}

            await websocket.send_json({"history": history, "conversation_id": conversation_id})
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})
