# DevGraph Copilot – Code Flow

## 1. Phase 1 – Basic health endpoint

- Client sends `GET /`.
- FastAPI handles the request in `app.main.read_root`.
- Returns static JSON with a simple Phase 1 message so you can test the server.

## 2. Phase 2 – Two-node LangGraph flow

- Client sends `POST /api/chat`.
- FastAPI builds an initial `GraphState` with at least `user_input`.
- LangGraph executes:
  - `planner_node`:
    - Reads `user_input`.
    - Sets a simple `message_type` to route the request.
  - `echo_node` (Phase 2):
    - Reads `user_input`.
    - Writes an echo-style `reply` back into the state.
- FastAPI returns `reply` from `GraphState` to the client.

## 3. Phase 3 – Fake RAG code-QA flow

- Client sends `POST /api/chat`.
- FastAPI builds `GraphState` with `user_input` (and any other default fields).
- LangGraph executes:
  1. `planner_node`:
     - Reads `user_input`.
     - Classifies and sets `message_type` (e.g., question vs statement).
  2. `code_qa_node`:
     - Calls `get_vector_store()` from `agents/ingestion_helper.py`.
     - Uses `dummy_embedding(user_input)` (Phase 3 fake RAG) to embed the query.
     - Searches `InMemoryVectorStore` for top matching chunks.
     - Writes `retrieved_chunks` and a `[Fake RAG]` style `reply` into the state.
- FastAPI returns `reply` (and, when needed for debugging or demo, `retrieved_chunks`) in the HTTP response.



High-level system view:
Document the runtime sequence for /api/chat:
Request enters FastAPI route in app/main.py.
Graph entry node receives message, wraps into graph state (graph_state.py).

Planner node:
Classifies message type (question vs others).
Chooses target_agent (currently code_qa).
Sets needs_ingestion flag based on last_ingestion_time and last_ingestion_source.

If needs_ingestion:
  Ingestion node calls init_or_refresh_vector_store() from ingestion_helper.py, which:
    Scans repo root, filters number of files based on the question.
    Chunks text, embeds with get_local_embedding_model(), builds vector store.


Code QA node:
Embeds user query, searches vector store, takes top-k chunks, calls LLM with retrieved context and guardrails to avoid hallucination.

