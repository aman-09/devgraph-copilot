# DevGraph Copilot – Interview Guide

> Use this document as a script to explain the project in interviews.

## 1. 60-second elevator pitch

DevGraph Copilot is a small agentic assistant for understanding code and project context.  
It uses a FastAPI backend, a LangGraph workflow, and a RAG pipeline built on local embeddings so it can work without external APIs.[web:221][web:236]  
The current version focuses on one main path: a planner node routes questions into a code-QA node, which retrieves relevant snippets and (optionally) calls an LLM to generate a clean answer.[web:221]  
The design is intentionally modular so new agents and MCP tools can be added later without changing the core request flow.[web:242]

## 2. How to explain the architecture

- FastAPI entrypoint:
  - `GET /` for health.
  - `POST /api/chat` to send user messages into the LangGraph workflow.[web:221]

- LangGraph workflow (current):
  - `planner_node` decides that the request should go to the code-QA branch.
  - `code_qa_node` performs retrieval and (optionally) calls the LLM.[web:221]

- RAG for code understanding:
  - Ingests sample/project text into an in-memory vector store.
  - Retrieves relevant chunks to ground answers and reduce hallucinations.[web:249]

- Future extensions:
  - More specialized agents (e.g., repo explorer, design explainer).
  - MCP tools for external actions (running commands, reading files, etc.).[web:244]

## 3. RAG, embeddings, and LLM strategy

- Embeddings:
  - Uses a **local sentence-transformers model via LangChain**, so retrieval works offline and does not depend on any external API.[web:236]
  - This replaces the earlier “fake RAG” phase that used dummy embeddings and a simple in-memory store.[web:249]

- LLM layer:
  - Implemented as a pluggable adapter (LangChain `ChatOpenAI` or similar).
  - Can point to a free-tier hosted LLM or a local model with a small config change.[web:236]

- End-to-end RAG + LLM path:
  1. User calls `/api/chat` with a question.
  2. `planner_node` classifies the message and routes to code-QA.
  3. `code_qa_node`:
     - Embeds the question using the local sentence-transformers model.
     - Retrieves top‑K chunks from the in-memory vector store.
     - Calls the chat model via LangChain with those chunks as context.
  4. The LLM returns a grounded natural answer, which is sent back to the client.[web:236][web:221]

## 4. Local vs API modes

- Embeddings:
  - Always local (sentence-transformers), so RAG retrieval is fully offline.[web:236]

- LLM modes (controlled by a simple config flag, e.g., `USE_LLM`):
  - `USE_LLM = false`:
    - System runs in **RAG-only mode**.
    - Returns retrieved snippets and a structured explanation without calling an external LLM.
  - `USE_LLM = true` (with valid API key):
    - Same node calls a hosted LLM via LangChain.
    - Generates a fluent answer on top of the retrieved context.[web:236]

- Demo advantage:
  - Can first show pure local RAG (no external dependency).
  - Then switch to full RAG + LLM with one configuration change and no code changes, which is a strong talking point in interviews.[memory:213][web:225]

## 5. Cross-question scenarios (planned)

These are the kinds of follow-up questions to practice:

- How do you handle large repos?
  - Talk about chunking strategy, indexing, and possibly moving from in-memory to a persistent vector store.[web:249]

- How do you reduce hallucinations?
  - Emphasize retrieval-first design, showing retrieved chunks, and keeping LLM prompts grounded in context.[web:236]

- How do you add a new agent?
  - Explain how a new node would be added to the LangGraph, how it reads/writes `GraphState`, and how the planner routes to it.[web:221]

- How do you secure write operations?
  - Mention separating read-only tools from write tools, adding explicit confirmations, and using role-based checks before executing actions.[web:244]
