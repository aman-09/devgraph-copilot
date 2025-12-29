# DevGraph Copilot – Architecture

> This document grows as the project evolves.

## 1. High-Level Overview

- FastAPI (`app/main.py`) exposes:
  - `GET /` – health/info endpoint.
  - `POST /api/chat` – main entry to the LangGraph workflow.
- LangGraph (`agents/graph_builder.py`) defines a stateful graph:
  - Nodes: `planner_node`, `code_qa_node`.
  - Flow: `START -> planner_node -> code_qa_node -> END`.
- RAG components (`rag/`) provide:
  - Simple chunking, dummy embeddings, and an in-memory vector store.

## 2. Current Status (up to Phase 3)

- State (`GraphState`) includes:
  - `user_input`, `message_type`, `reply`, `retrieved_chunks`.
- Fake RAG:
  - `agents/ingestion_helper.py` initializes an in-memory vector store with sample text.
  - `code_qa_node`:
    - Embeds `user_input` with `dummy_embedding`.
    - Searches `InMemoryVectorStore`.
    - Returns retrieved snippets and a `[Fake RAG]` style reply.

- Embeddings:
  - Local sentence-transformers model (`all-MiniLM-L6-v2`) via LangChain's HuggingFaceEmbeddings.
  - No external API required for RAG; everything runs locally.


