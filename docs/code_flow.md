# DevGraph Copilot – Code Flow

## 1. Phase 1 – Request Flow

- Client sends GET `/`
- FastAPI handles the request in `app.main.read_root`
- Returns static JSON with a Phase 1 message

## 2. Phase 2 – Two-Node LangGraph Flow

- Client calls `POST /api/chat`.
- FastAPI builds `GraphState` with `user_input`.
- LangGraph runs:
  - `planner_node` -> sets `message_type`.
  - `echo_node` (Phase 2) -> sets `reply`.

## 3. Phase 3 – Fake RAG Code-QA Flow

- Client calls `POST /api/chat`.
- FastAPI builds `GraphState` with `user_input`.
- LangGraph runs:
  1. `planner_node`:
     - Reads `user_input`.
     - Sets `message_type` (question/statement).
  2. `code_qa_node`:
     - Calls `get_vector_store()` from `agents/ingestion_helper.py`.
     - Uses `dummy_embedding(user_input)` to embed query.
     - Searches `InMemoryVectorStore` for top chunks.
     - Writes `retrieved_chunks` and a `[Fake RAG]` reply into state.
- FastAPI returns `reply` (and optionally `retrieved_chunks`).

