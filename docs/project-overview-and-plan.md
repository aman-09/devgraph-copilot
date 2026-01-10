# DevGraph Copilot – Project Overview and Plan

## 1. What this project is

DevGraph Copilot is a small agentic assistant to help understand code and project context.  
It exposes a FastAPI endpoint that sends user questions into a LangGraph workflow, which then uses a RAG pipeline (on local embeddings) and an optional LLM to produce answers.

The goal is to be **interview-friendly**: the project is small enough to explain in a few minutes but rich enough to show real agentic patterns (planner, RAG, future tools/MCP).

## 2. Why this project exists

- To demonstrate understanding of:
  - FastAPI backends and clean API design.
  - LangGraph-style agent workflows and shared state.
  - Retrieval-Augmented Generation (RAG) with local embeddings.
  - Swapping between local-only and API-based LLM modes.

- To serve as a live demo:
  - Can be run locally on a laptop.
  - Can be walked through step-by-step in an interview (phases, code, docs).

## 3. Current feature set (today)

- FastAPI service with:
  - `GET /` health check.
  - `POST /api/chat` main entrypoint.

- LangGraph workflow:
  - `planner_node` for simple routing / message classification.
  - `code_qa_node` that performs retrieval and (optionally) calls an LLM.

- RAG pipeline:
  - Local sentence-transformers embeddings (`all-MiniLM-L6-v2`) via LangChain.
  - In-memory vector store with sample/project text.
  - Code-QA answers that include `retrieved_chunks` for transparency.

- Configuration:
  - Simple flag to run in “RAG-only” or “RAG + LLM” mode depending on API key.

## 4. Phase plan

- **Phase 1 – Skeleton API**
  - Basic FastAPI app with `GET /` and placeholder `POST /api/chat`.
  - Simple echo behavior to verify request/response wiring.

- **Phase 2 – Basic LangGraph**
  - Introduce `GraphState`.
  - Add `planner_node` and a simple `echo_node`.
  - Show a minimal two-node graph working end-to-end.

- **Phase 3 – RAG-powered Code-QA** ✅ (current)
  - Add RAG components (`rag/`, `agents/ingestion_helper.py`).
  - Ingest sample text; move from fake RAG to local embeddings.
  - Implement `code_qa_node` that retrieves chunks and calls an LLM adapter.

- **Phase 4 – More agents + MCP (planned)**
  - Add specialized agents (e.g., repo explorer, design explainer).
  - Integrate MCP tools for actions like reading files or running commands.
  - Extend planner logic to route to multiple agents.

## 5. Next steps (short roadmap)

Near-term improvements:

- Make planner smarter (use metadata to avoid re-running ingestion on every request).
- Add one concrete MCP-style or tool-based node (e.g., file reader agent).
- Flesh out docs:
  - `architecture.md` kept as a living system diagram.
  - `code_flow.md` showing request paths per phase.
  - `interview_guide.md` with ready-to-say answers for common questions.



Summarize the current milestone and next ones:
Current status:
End-to-end agentic RAG working on local repo with ingestion, planner, and QA.

Next milestones:
Improve retrieval (chunking & top_k).
Add specialized agents (design explainer, tests agent, documentation agent).
Better observability (log retrieved chunks, add simple metrics).





