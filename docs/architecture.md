# DevGraph Copilot – Architecture

> Living document: this file is updated as the project evolves, but stays short and high level.[web:219]

## 1. High-level overview

- **FastAPI layer** (`app/main.py`):
  - `GET /` – simple health/info endpoint to verify the service is up.
  - `POST /api/chat` – main entrypoint into the LangGraph workflow.[web:221]

- **LangGraph workflow** (`agents/graph_builder.py`):
  - Nodes: `planner_node`, `code_qa_node`.
  - Flow (current): `START -> planner_node -> code_qa_node -> END`.
  - The graph is stateful: each node reads and writes a shared `GraphState`.[web:221]

- **RAG components** (`rag/`):
  - Provide text chunking, embeddings, and an in-memory vector store.
  - Start as “fake RAG” with dummy embeddings and then switch to local sentence-transformers.[web:249]

## 2. Graph state and data flow (Phase 3)

- **GraphState fields** (current):
  - `user_input`: the latest user message.
  - `message_type`: simple routing hint (e.g., “general”, “code_qa”).
  - `reply`: the final natural language answer returned to the client.
  - `retrieved_chunks`: snippets retrieved by the RAG pipeline for transparency.[web:221]

- **Planner node** (`planner_node`):
  - Reads `user_input` and `message_type`.
  - Decides that the request should go to the code QA branch (current simple routing).
  - For now, forwards to `code_qa_node` without modifying RAG state.[web:221]

- **Code-QA node** (`code_qa_node`):
  - Takes `user_input`, performs retrieval over the vector store, and calls the LLM.
  - Writes the final answer into `reply` and the used context into `retrieved_chunks`.[web:221][web:236]

## 3. RAG and embeddings

- **Initial fake RAG**:
  - `agents/ingestion_helper.py` initializes an in-memory vector store with sample text.
  - A dummy embedding function converts text to simple numeric vectors.
  - `code_qa_node`:
    - Embeds `user_input` with `dummy_embedding`.
    - Searches `InMemoryVectorStore`.
    - Produces a `[Fake RAG]` style reply with retrieved snippets.[web:249]

- **Current embeddings setup**:
  - Uses a local sentence-transformers model (`all-MiniLM-L6-v2`) via LangChain’s `HuggingFaceEmbeddings`.
  - No external API is required for RAG; all embedding and retrieval run locally.[web:236]

- **Code-QA with local RAG (Phase 3+)**:
  - Uses local embeddings from `sentence-transformers` to query the vector store.
  - Calls an LLM (via LangChain `ChatOpenAI`) with `retrieved_chunks` as context.
  - Returns a natural language answer in `reply`, suitable to send directly to the frontend.[web:236]
