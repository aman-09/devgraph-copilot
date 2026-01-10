from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings
from agents.graph_builder import graph_app
from agents.graph_state import GraphState

import logging

logging.basicConfig(level=logging.INFO)



class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    retrieved_chunks: Optional[List[str]] = None
    file_content: Optional[str] = None


app = FastAPI(title=f"{settings.app_name} - Phase 2")


@app.get("/")
async def read_root():
    return {
        "message": "DevGraph Copilot backend is running (Phase 3 - Fake RAG)",
        "next_steps": [
            "Replace dummy embeddings with real embeddings",
            "Ingest real repository content instead of sample text",
            "Add true LLM-based Code-QA agent and more agents",
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
    chunks = result_state.get("retrieved_chunks", [])
    file_content = result_state.get("file_content", "")

    return ChatResponse(
        reply=reply_text,
        retrieved_chunks=chunks,
        file_content=file_content,
    )
    

from agents.ingestion_helper import get_vector_store
from rag.embeddings import embed_text
from agents.code_qa_chain import explain_design_with_context


class DesignExplainRequest(BaseModel):
    message: str

class DesignExplainResponse(BaseModel):
    reply: str
    retrieved_chunks: List[str]


@app.post("/api/design-explain", response_model=DesignExplainResponse)
async def design_explain_endpoint(request: DesignExplainRequest):
    """
    Test endpoint to exercise explain_design_with_context using the same RAG pipeline.
    """
    user_input = request.message

    # 1) RAG retrieval (same as code_qa_node)
    store = get_vector_store()
    query_emb = embed_text(user_input)
    top_chunks = store.search(query_emb, top_k=3)
    retrieved_texts = [c.text for c in top_chunks]

    # 2) Design-style LLM answer
    answer = explain_design_with_context(user_input, retrieved_texts)

    return DesignExplainResponse(
        reply=answer,
        retrieved_chunks=retrieved_texts,
    )




# This is the absolute minimum FastAPI app.

# What changed:
# New ChatRequest and ChatResponse models (JSON in/out).
# Root / now says “Phase 2”.
# New endpoint /api/chat that:
#     Builds initial state.
#     Calls graph_app.invoke(initial_state).
#     Returns reply.