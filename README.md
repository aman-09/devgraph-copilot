# DevGraph Copilot

Developer Productivity Copilot for GitHub repositories, built with **FastAPI**, **LangGraph**, **LangChain**, **MCP**, and **RAG**.

This project is designed as a full learning path: starting from a simple FastAPI app and growing into a multi‑agent, production‑style Agentic AI system.

---

## 1. Project Setup (All Phases)

### 1.1 Clone and enter the project
if this is your own repo
git clone <your_repo_url> devgraph-copilot
cd devgraph-copilot

If you are starting locally without git yet, just create a folder named `devgraph-copilot` and follow the rest of the steps.

### 1.2 Create and activate virtual environment
python -m venv .venv

Windows:
.venv\Scripts\activate

macOS / Linux:
source .venv/bin/activate



### 1.3 Install dependencies
pip install -r requirements.txt

> Requirements will grow as we move through phases. At minimum, this project uses FastAPI, Uvicorn, LangChain, LangGraph, pydantic‑settings, and some helper libraries.


### 1.4 Run the app
uvicorn app.main:app --reload

Open in browser:

- http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

---

## 2. Project Folder Structure (High Level)

As the project grows, the structure will look like this:

devgraph-copilot/
├── app
│   ├── __init__.py
│   ├── main.py              # FastAPI app entrypoint (routes, wiring)
│   └── config.py            # Settings and configuration (env, keys, etc.)
│
├── agents
│   ├── __init__.py
│   ├── graph_state.py       # Shared LangGraph state (query, plan, docs, etc.)
│   ├── graph_builder.py     # LangGraph graph definition (nodes, edges)
│   ├── planner.py           # Planner agent (decides which agents to run)
│   ├── ingestion.py         # Ingestion agent (clone repo, chunk, embed, index)
│   ├── data_quality.py      # Data quality agent (sanity checks on data/index)
│   ├── code_qa.py           # RAG-based code QA agent (answer questions)
│   ├── tool_executor.py     # MCP tool executor agent (call external tools)
│   └── documentation_agent.py  # Example extra agent (docs generator)
│
├── rag
│   ├── __init__.py
│   ├── chunking.py          # Chunking strategies for RAG
│   ├── embeddings.py        # Embedding model wrapper
│   └── vectorstore.py       # Vector store abstraction (add/search)
│
├── mcp_servers
│   ├── __init__.py
│   ├── repo_tools           # MCP server for repo operations (list/read/write)
│   └── external_tools       # MCP server for external APIs (weather/news/etc.)
│
├── tests
│   └── test_main.py         # Unit/integration tests (will grow later)
│
├── docs
│   ├── project-overview-and-plan.md
│   ├── architecture.md
│   ├── code_flow.md
│   ├── how_to_add_an_agent.md
│   ├── example_new_agent_documentation_agent.md
│   └── interview_guide.md
│
├── requirements.txt
├── Dockerfile               # For deployment (later phase)
└── README.md



Each phase will fill in more files so the folder structure gradually matches this full picture.

---

## 3. Phase 1 – Minimal FastAPI Backend

**Goal:** Confirm the backend can start and respond to a simple request.

### 3.1 Files created in Phase 1

- `app/main.py`
- `app/__init__.py`
- `agents/__init__.py`
- `rag/__init__.py`
- `mcp_servers/__init__.py`
- `requirements.txt`
- `README.md`

### 3.2 Code (Phase 1)

`app/main.py` (Phase 1 version) was:

from fastapi import FastAPI

FastAPI application instance
app = FastAPI(title="DevGraph Copilot - Phase 1")

@app.get("/")
async def read_root():
return {
"message": "DevGraph Copilot backend is running (Phase 1)",
"next_steps": [
"Add LangGraph state graph",
"Add basic RAG pipeline",
"Integrate MCP tools"
]
}



### 3.3 How to run Phase 1

From the project root:
uvicorn app.main:app --reload

Open in browser:
- http://127.0.0.1:8000

Expected JSON (Phase 1):
{
"message": "DevGraph Copilot backend is running (Phase 1)",
"next_steps": [
"Add LangGraph state graph",
"Add basic RAG pipeline",
"Integrate MCP tools"
]
}


If you saw this response, Phase 1 was working.

---

## 4. Phase 2 – LangGraph Skeleton

**Goal:** Wire a minimal LangGraph graph into the FastAPI backend.

### 4.1 New / updated files in Phase 2

- `app/config.py` – Basic settings (app name, environment).
- `agents/graph_state.py` – Shared state definition for the graph.
- `agents/graph_builder.py` – Minimal LangGraph graph with planner and echo nodes.
- `app/main.py` – Updated to:
  - Show “Phase 2” at `/`
  - Add `POST /api/chat` endpoint that uses LangGraph.

### 4.2 State and nodes (current)

`GraphState` fields:

- `user_input`: raw message from API.
- `message_type`: simple classification (e.g., `"question"` or `"statement"`).
- `reply`: final reply text.

Nodes:

- `planner_node`:
  - Reads `user_input`.
  - Sets `message_type` to `"question"` if it ends with `?`, otherwise `"statement"`.
- `echo_node`:
  - Reads `user_input` and `message_type`.
  - Writes `reply` including both.

Graph flow:
START -> planner_node -> echo_node -> END


### 4.3 New endpoint – `POST /api/chat`

**Request body:**
{
"message": "hello"
}


**Response (example):**
{
"reply": "Echo from LangGraph (type=statement): you said -> hello"
}



**How it works (short):**

1. FastAPI receives the request in `/api/chat`.
2. It creates an initial `GraphState` with `user_input`.
3. It calls the compiled LangGraph `graph_app`.
4. `planner_node` sets `message_type`.
5. `echo_node` reads `user_input` and `message_type` and writes `reply`.
6. The final state is returned as the HTTP response.

### 4.4 Test the two‑node flow

1. Restart server:
uvicorn app.main:app --reload

2. Open Swagger: http://127.0.0.1:8000/docs

3. Test `POST /api/chat`:

- Body:
{ "message": "how are you?" }


Expected:
{
"reply": "Echo from LangGraph (type=question): you said -> how are you?"
}


- Body:
{ "message": "this is a statement" }


Expected:
{
"reply": "Echo from LangGraph (type=statement): you said -> this is a statement"
}



This proves:

- State is flowing through multiple nodes.
- Planner writes `message_type`, echo reads it.

---

## 5. Phase 3 – RAG Skeleton (Setup Only)

**Goal:** Create basic files for RAG components (no real LLM yet).

### 5.1 New files in Phase 3 (skeleton)

- `rag/chunking.py`
- `simple_line_chunker(text: str) -> List[str>` – trivial line-based chunker.

- `rag/embeddings.py`
- `dummy_embedding(text: str) -> List[float]` – fake embedding based on length.
- `embed_chunks(chunks: List[str]) -> List[List[float]]`.

- `rag/vectorstore.py`
- `InMemoryVectorStore` – in-memory store of chunks and fake embeddings.
- `add(chunks, embeddings)` and `search(query_embedding, top_k=3)`.

### 5.2 Current status

These modules are not yet wired into the graph or API.  
They are placeholders to make Phase 3 integration easier.

---

## 6. Summary of Phase 1 and Phase 2

**Phase 1**

- Basic FastAPI app with `GET /` returning Phase 1 JSON.
- `requirements.txt`, virtualenv, minimal project structure.

**Phase 2 (plus tiny 2-node upgrade)**

- `app/config.py` with `Settings`.
- `agents/graph_state.py` defining `GraphState` (`user_input`, `message_type`, `reply`).
- `agents/graph_builder.py` with a LangGraph `StateGraph`:
- Nodes: `planner_node → echo_node`.
- Flow: `START → planner_node → echo_node → END`.
- `app/main.py` updated:
- Root `/` shows “Phase 2”.
- New `POST /api/chat` endpoint using `graph_app.invoke`.

**RAG skeleton files created (but not yet used):**

- `rag/chunking.py`
- `rag/embeddings.py`
- `rag/vectorstore.py`

If `/` returns Phase 2 JSON and `POST /api/chat` returns the echo with the correct `type=question/statement`, you are fully done with these phases and ready to start wiring real RAG and more agents next.

---
