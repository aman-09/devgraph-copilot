from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings
from agents.graph_builder import graph_app
from agents.graph_state import GraphState


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title=f"{settings.app_name} - Phase 2")


@app.get("/")
async def read_root():
    return {
        "message": "DevGraph Copilot backend is running (Phase 2)",
        "next_steps": [
            "Add real LLM-backed agent logic",
            "Add RAG (chunking + embeddings)",
            "Integrate MCP tools"
        ],
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Simple chat endpoint that sends the input through a minimal LangGraph graph.
    """
    # Initial state for the graph
    initial_state: GraphState = {"user_input": request.message}

    # Call the graph synchronously for Phase 2
    result_state: GraphState = graph_app.invoke(initial_state)

    # Extract reply
    reply_text = result_state.get("reply", "")

    return ChatResponse(reply=reply_text)



# This is the absolute minimum FastAPI app.

# What changed:
# New ChatRequest and ChatResponse models (JSON in/out).
# Root / now says “Phase 2”.
# New endpoint /api/chat that:
#     Builds initial state.
#     Calls graph_app.invoke(initial_state).
#     Returns reply.