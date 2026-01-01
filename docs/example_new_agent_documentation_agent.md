# Example Agent – DocumentationAgent (Planned)

This document will eventually walk through creating a `DocumentationAgent` from scratch, step by step, so it can be used as a template for future agents.

Planned sections:

1. **Problem statement and requirements**
   - What DocumentationAgent should do (e.g., answer “how is this component wired?” using project docs and code).

2. **Extending `GraphState`**
   - New fields needed (e.g., `doc_query`, `doc_context`, `doc_answer`).

3. **Using RAG for docs and code**
   - Chunking and indexing project documentation and code comments.
   - Choosing embeddings and vector store for this agent.

4. **Implementing the LangChain chain**
   - Prompt design for documentation-style answers.
   - How the chain combines retrieved context and user questions.

5. **Wrapping the agent as a LangGraph node**
   - Node function signature.
   - Reading/writing the right `GraphState` fields.
   - Handling errors and empty results.

6. **Integrating with MCP tools (optional)**
   - Using tools to read files, list docs, or fetch external references.
   - How the node decides when to call a tool vs. only RAG.

7. **Tests and demo flow**
   - Unit tests for the chain and retrieval logic.
   - End-to-end demo script: example questions, expected behavior, and how to present this agent in an interview.
