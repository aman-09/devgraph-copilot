# DevGraph Copilot – Interview Guide

> Use this document as a script to explain the project in interviews.

## 1. 60-second elevator pitch

DevGraph Copilot is a small agentic assistant for understanding code and project context.  
It uses a FastAPI backend, a LangGraph workflow, and a RAG pipeline built on local embeddings so it can work without external APIs.  
The current version focuses on one main path: a planner node routes questions into a code-QA node, which retrieves relevant snippets and (optionally) calls an LLM to generate a clean answer.  
The design is intentionally modular so new agents and MCP tools can be added later without changing the core request flow.

## 2. How to explain the architecture

- FastAPI entrypoint:
  - `GET /` for health.
  - `POST /api/chat` to send user messages into the LangGraph workflow.

- LangGraph workflow (current):
  - `planner_node` decides that the request should go to the code-QA branch.
  - `code_qa_node` performs retrieval and (optionally) calls the LLM.

- RAG for code understanding:
  - Ingests sample/project text into an in-memory vector store.
  - Retrieves relevant chunks to ground answers and reduce hallucinations.

- Future extensions:
  - More specialized agents (e.g., repo explorer, design explainer).
  - MCP tools for external actions (running commands, reading files, etc.).

## 3. RAG, embeddings, and LLM strategy

- Embeddings:
  - Uses a **local sentence-transformers model via LangChain**, so retrieval works offline and does not depend on any external API.
  - This replaces the earlier “fake RAG” phase that used dummy embeddings and a simple in-memory store.

- LLM layer:
  - Implemented as a pluggable adapter (LangChain `ChatOpenAI` or similar).
  - Can point to a free-tier hosted LLM or a local model with a small config change.

- End-to-end RAG + LLM path:
  1. User calls `/api/chat` with a question.
  2. `planner_node` classifies the message and routes to code-QA.
  3. `code_qa_node`:
     - Embeds the question using the local sentence-transformers model.
     - Retrieves top‑K chunks from the in-memory vector store.
     - Calls the chat model via LangChain with those chunks as context.
  4. The LLM returns a grounded natural answer, which is sent back to the client.

The planner uses ingestion metadata (last_ingestion_time, last_ingestion_source) stored in the graph state to avoid re-ingesting documents on every request.

Talking point:
Initially, ingestion ran on every request. Later, ingestion was split into a separate step and the planner started checking whether the current vector store is fresh enough. This reduced unnecessary work and is closer to how production RAG systems manage indexing vs. query-time retrieval.


### Ingestion strategy and planner decisions

Initially, ingestion ran on every request and rebuilt the in-memory vector store each time.  
Later, ingestion was separated into its own node and the planner started using **ingestion metadata** stored in `GraphState` (`last_ingestion_time`, `last_ingestion_source`).

For each new request, the planner checks this metadata to decide whether ingestion is needed.  
If the vector store is fresh enough (for example, ingested within the last 30 minutes), the planner lets the request go directly to the code-QA node, skipping ingestion.

This demonstrates a core **agentic RAG** idea: agents use state and metadata to avoid unnecessary work and to separate indexing (ingestion) from query-time retrieval.


### Simple tool-style agent: file reader

I added a small **file-reader node** as a first tool-style agent.  
Before planning and RAG, this node reads a local text file from the `sample_data` folder (for example `info.txt`) and stores its content in the shared `GraphState` as `file_content`.

The rest of the graph then runs as usual: the planner classifies the message, ingestion ensures the vector store is ready, and the code-QA node does retrieval and answering.  
This demonstrates how agents in the graph can call simple tools (like reading a file) and pass their results forward through state before the main RAG flow runs.

With this, I can say that my system already has:
- A planner node.
- A RAG-based code-QA node.
- A simple tool-style agent (file reader) that shows how to integrate external data into the state before answering.


### Planner routing between agents

The planner does more than just classify messages; it also decides **which agent to route to** using a simple `target_agent` flag in the shared `GraphState`.

For normal questions, the planner sets `target_agent="code_qa"`, so the request flows into the RAG-based code-QA node.  
For messages that look like file-related requests (for example, containing words like “file” or “read info”), the planner can set `target_agent="file_reader"`, which is the first step towards routing to different tool-style agents from the same planner.




## 4. Local vs API modes

- Embeddings:
  - Always local (sentence-transformers), so RAG retrieval is fully offline.

- LLM modes (controlled by a simple config flag, e.g., `USE_LLM`):
  - `USE_LLM = false`:
    - System runs in **RAG-only mode**.
    - Returns retrieved snippets and a structured explanation without calling an external LLM.
  - `USE_LLM = true` (with valid API key):
    - Same node calls a hosted LLM via LangChain.
    - Generates a fluent answer on top of the retrieved context.

- Demo advantage:
  - Can first show pure local RAG (no external dependency).
  - Then switch to full RAG + LLM with one configuration change and no code changes, which is a strong talking point in interviews.

## 5. Cross-question scenarios (planned)

These are the kinds of follow-up questions to practice:

- How do you handle large repos?
  - Talk about chunking strategy, indexing, and possibly moving from in-memory to a persistent vector store.

- How do you reduce hallucinations?
  - Emphasize retrieval-first design, showing retrieved chunks, and keeping LLM prompts grounded in context.

- How do you add a new agent?
  - Explain how a new node would be added to the LangGraph, how it reads/writes `GraphState`, and how the planner routes to it.

- How do you secure write operations?
  - Mention separating read-only tools from write tools, adding explicit confirmations, and using role-based checks before executing actions.
