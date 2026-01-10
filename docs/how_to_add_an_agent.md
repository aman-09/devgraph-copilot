# How to Add a New Agent

> Use this as a checklist when adding a new node/agent to the LangGraph workflow.

## 1. High-level steps

1. **Define the agent’s responsibility**
   - Example: “Repo explainer”, “Design Q&A”, “Refactoring suggester”.
   - Write this in one or two sentences before you start coding.

2. **Decide GraphState fields to read/write**
   - List which keys the agent needs to read (e.g., `user_input`, `retrieved_chunks`).
   - Decide what it will write back (e.g., `reply`, `analysis`, `tool_results`).

3. **Implement the core logic (chain/tools/RAG)**
   - Build a LangChain chain or tool wrapper that does the real work:
     - Prompt + LLM.
     - Optional RAG (retrieval over vector store).
     - Optional MCP/tool calls.
   - Keep this logic independent from LangGraph so it can be tested alone.

4. **Wrap the logic in a LangGraph node function**
   - Create a node function like `def my_agent_node(state: GraphState) -> GraphState:`.
   - Inside the node:
     - Read the needed fields from `state`.
     - Call the chain/tools.
     - Update `state` with new fields (e.g., `reply`, `retrieved_chunks`).

5. **Register the node and edges in `graph_builder.py`**
   - Add the node to the graph with a clear name (e.g., `"repo_explainer_node"`).
   - Update edges so the planner (or previous node) can route into it:
     - Either from `planner_node` directly.
     - Or after another node, depending on your flow.

6. **Add tests and update docs**
   - Add unit tests for the core logic (without LangGraph).
   - Add at least one integration-style test that runs the graph through the new node.
   - Update:
     - `architecture.md` (where the new agent sits in the system).
     - `code_flow.md` (how a request reaches this agent).
     - `interview_guide.md` (one or two sentences on what this agent does).

## 2. Existing example nodes

- **`planner_node`**:
  - Reads: `user_input`.
  - Writes: `message_type` (simple classification / routing hint).

- **`code_qa_node`**:
  - Reads: `user_input`, `message_type`.
  - Uses RAG helpers from `rag/` and `agents/ingestion_helper.py`.
  - Writes: `retrieved_chunks`, `reply`.

New agents should follow the same pattern: read from `GraphState`, call their own logic or tools, write updates back to `GraphState`, and get wired into the graph in `graph_builder.py` with clear edges from the planner or other nodes.



High-level system view:
current graph understanding into a step-by-step guide:

Steps:
1. Create a new handler function in agents/code_qa_chain.py or a new file for the agent logic.
2. Register a node in agents/graph_builder.py StateGraph.
3. ​Update planner to select the new target_agent based on message intent.
4. Optionally, define any extra tools or vector filters this agent will use.
5. ​Add tests or sample prompts in docs.