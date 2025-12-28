# How to Add a New Agent

> This is the template. Detailed example will be filled after core graph is ready.

## 1. Steps (High Level)

1. Define responsibility of the new agent.
2. Decide `GraphState` fields to read/write.
3. Implement a LangChain chain (prompt, tools, RAG if needed).
4. Wrap chain in a LangGraph node function.
5. Register the node and edges in `graph_builder.py`.
6. Add tests and update docs.

Detailed, code-level examples will be added after Phase 3.
