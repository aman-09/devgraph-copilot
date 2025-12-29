# DevGraph Copilot – Interview Guide

> Use this document to explain the project in interviews.

## 1. 60-Second Elevator Pitch

(To be filled after core features are implemented.)

## 2. How to Explain the Architecture

- FastAPI entrypoint.
- LangGraph multi-agent workflow (coming in Phase 2+).
- RAG for code understanding (coming in Phase 3+).
- MCP tools for external actions (coming in Phase 4+).
- Currently, the Code-QA part uses a fake RAG:
  - Sample text is ingested into an in-memory store.
  - Queries are embedded with a dummy function.
  - Top chunks are returned and used to build a simple `[Fake RAG]` reply.
  - This is a teaching step before plugging in real embeddings and LLMs.

### RAG, Embeddings, and LLM Strategy
For embeddings I use a **local sentence-transformers model via LangChain**, so the RAG pipeline works offline and does not depend on any external API.

The LLM layer is **pluggable**; right now I use a free-tier hosted LLM, but the architecture supports swapping to any provider or even a fully local model by changing a small adapter layer.


## 3. Cross-Question Scenarios (Planned)

- How do you handle large repos?
- How do you reduce hallucinations?
- How do you add a new agent?
- How do you secure write operations?

Each question will later get:
- A suggested answer.
- References to the relevant files to modify.
