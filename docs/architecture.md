# DevGraph Copilot – Architecture

> Living document: this file is updated as the project evolves, but stays short and high level.

## 1. High-level overview

- **FastAPI layer** (`app/main.py`):
  - `GET /` – simple health/info endpoint to verify the service is up.
  - `POST /api/chat` – main entrypoint into the LangGraph workflow.

- **LangGraph workflow** (`agents/graph_builder.py`):
  - Nodes: `planner_node`, `code_qa_node`.
  - Flow (current): `START -> planner_node -> code_qa_node -> END`.
  - The graph is stateful: each node reads and writes a shared `GraphState`.

- **RAG components** (`rag/`):
  - Provide text chunking, embeddings, and an in-memory vector store.
  - Start as “fake RAG” with dummy embeddings and then switch to local sentence-transformers.

## 2. Graph state and data flow (Phase 3)

- **GraphState fields** (current):
  - `user_input`: the latest user message.
  - `message_type`: simple routing hint (e.g., “general”, “code_qa”).
  - `reply`: the final natural language answer returned to the client.
  - `retrieved_chunks`: snippets retrieved by the RAG pipeline for transparency.

- **Planner node** (`planner_node`):
  - Reads `user_input` and `message_type`.
  - Decides that the request should go to the code QA branch (current simple routing).
  - For now, forwards to `code_qa_node` without modifying RAG state.

- **Code-QA node** (`code_qa_node`):
  - Takes `user_input`, performs retrieval over the vector store, and calls the LLM.
  - Writes the final answer into `reply` and the used context into `retrieved_chunks`.

## 3. RAG and embeddings

- **Initial fake RAG**:
  - `agents/ingestion_helper.py` initializes an in-memory vector store with sample text.
  - A dummy embedding function converts text to simple numeric vectors.
  - `code_qa_node`:
    - Embeds `user_input` with `dummy_embedding`.
    - Searches `InMemoryVectorStore`.
    - Produces a `[Fake RAG]` style reply with retrieved snippets.

- **Current embeddings setup**:
  - Uses a local sentence-transformers model (`all-MiniLM-L6-v2`) via LangChain’s `HuggingFaceEmbeddings`.
  - No external API is required for RAG; all embedding and retrieval run locally.

- **Code-QA with local RAG (Phase 3+)**:
  - Uses local embeddings from `sentence-transformers` to query the vector store.
  - Calls an LLM (via LangChain `ChatOpenAI`) with `retrieved_chunks` as context.
  - Returns a natural language answer in `reply`, suitable to send directly to the frontend.



  Planner routing and Design Explainer node
DevGraph Copilot uses a simple planner to route user requests through different agents in the LangGraph workflow. The current graph supports:

A Code QA agent for standard RAG-style answers.

A Design Explainer agent for interview-style architecture explanations.

Planner routing
The planner_node inspects the user_input and sets a target_agent in GraphState:

If the message contains design keywords (e.g. "architecture", "system design", "design explain"), it routes to the Design Explainer:

target_agent = "design_explainer".

If the message mentions "read info" or "file", it routes to the File Reader:

target_agent = "file_reader".

Otherwise, it defaults to the Code QA agent:

target_agent = "code_qa".

The planner also sets message_type ("question" vs "statement") and flags needs_ingestion, which controls whether the ingestion node rebuilds the vector store.

Graph flow
The compiled LangGraph pipeline is:

START → file_reader_node → planner_node → ingestion_node → code_qa_node → design_explainer_node → END

For every request:

file_reader_node can load sample_data/info.txt when appropriate.

planner_node decides which agent should ultimately answer.

ingestion_node ensures the vector store is initialized/refreshed from sample_data.

code_qa_node always:

Embeds user_input.

Runs vector search.

Produces a QA-style reply when use_llm is enabled (Groq) or a RAG-only reply when disabled.

design_explainer_node:

Reuses retrieved_chunks from code_qa_node.

If target_agent == "design_explainer" and LLM is enabled, calls explain_design_with_context to overwrite reply with a system-design-style explanation.

Otherwise, it effectively passes through the QA reply unchanged.

This setup lets the same RAG backbone serve both normal “bug/feature” questions and higher-level “explain the architecture” prompts without changing the client API.
