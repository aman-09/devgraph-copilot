# graph_builder.py
import logging
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, START, END

from .graph_state import GraphState
from .ingestion_helper import get_vector_store, init_or_refresh_vector_store, INGESTION_RAN
from rag.embeddings import embed_text
from app.config import settings
from .code_qa_chain import answer_with_context, explain_design_with_context

logger = logging.getLogger(__name__)

INGESTION_MAX_AGE_MINUTES = 30  # simple policy for now


from pathlib import Path

def file_reader_node(state: GraphState) -> GraphState:
    # If planner (previous run) said we don't need file_reader, just pass through
    if state.get("target_agent") not in (None, "file_reader"):
        return state

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "sample_data"
    file_path = data_dir / "info.txt"

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        content = f"[file_reader_node] Failed to read {file_path}: {e}"

    new_state: GraphState = dict(state)
    new_state["file_content"] = content
    logger.info(
        "file_reader_node: read %d characters from %s",
        len(content),
        file_path,
    )
    return new_state




def planner_node(state: GraphState) -> GraphState:
    user_input = state.get("user_input", "")
    msg_type = "question" if user_input.strip().endswith("?") else "statement"

    text = user_input.lower()

    # New: simple design-intent detection
    if any(kw in text for kw in ["architecture", "system design", "design explain"]):
        target_agent = "design_explainer"
    elif "read info" in text or "file" in text:
        target_agent = "file_reader"
    else:
        target_agent = "code_qa"

    needs_ingestion = not INGESTION_RAN
    logger.info(
        "Planner: message_type=%s, target_agent=%s, needs_ingestion=%s, user_input='%s'",
        msg_type,
        target_agent,
        needs_ingestion,
        user_input,
    )

    new_state: GraphState = dict(state)
    new_state["message_type"] = msg_type
    new_state["needs_ingestion"] = needs_ingestion
    new_state["target_agent"] = target_agent
    return new_state




def ingestion_node(state: GraphState) -> GraphState:
    needs_ingestion = state.get("needs_ingestion", True)
    if not needs_ingestion:
        logger.info("Ingestion node: needs_ingestion=False, skipping ingestion.")
        return state

    logger.info("Ingestion node: running ingestion and rebuilding vector store.")
    init_or_refresh_vector_store()

    new_state: GraphState = dict(state)
    new_state["last_ingestion_time"] = datetime.utcnow().isoformat()
    new_state["last_ingestion_source"] = "sample_data"
    logger.info(
        "Ingestion node: updated last_ingestion_time=%s, last_ingestion_source=%s.",
        new_state["last_ingestion_time"],
        new_state["last_ingestion_source"],
    )
    return new_state


# The behavior now:
# First request: last_ingestion_time is missing → planner sets needs_ingestion=True → ingestion runs and writes metadata → code_qa runs.
# Later requests (within 30 minutes): planner sets needs_ingestion=False → ingestion node becomes a no-op → code_qa runs directly.


def code_qa_node(state: GraphState) -> GraphState:
    """
    Code-QA node using RAG, with optional LLM.

    - Always:
      - Embeds the user_input using local embeddings.
      - Searches the in-memory vector store.
    - If settings.use_llm is True:
      - Calls LLM with retrieved chunks as context to generate an answer.
    - Otherwise:
      - Returns a RAG-only answer composed from the retrieved snippets.
    """
    user_input = state.get("user_input", "")
    if not user_input:
        return {"reply": "I did not receive any input.", "retrieved_chunks": []}

    # 1) RAG retrieval (always)
    store = get_vector_store()
    query_emb = embed_text(user_input)
    top_chunks = store.search(query_emb, top_k=10)
    retrieved_texts = [c.text for c in top_chunks]
    logger.info("code_qa_node: retrieved_texts sample: %s", retrieved_texts[:3])


    # 2) If LLM disabled, return RAG-only answer
    if not settings.use_llm or not settings.groq_api_key:
        joined_snippets = " | ".join(retrieved_texts) if retrieved_texts else "No relevant text found."
        reply = (
            f"[RAG only] You asked: '{user_input}'. "
            f"Top snippets from knowledge base: {joined_snippets}"
        )
        return {
            "retrieved_chunks": retrieved_texts,
            "reply": reply,
        }

    # 3) LLM-enabled path
    try:
        llm_answer = answer_with_context(user_input, retrieved_texts)
        return {
            "retrieved_chunks": retrieved_texts,
            "reply": llm_answer,
        }
    except Exception as e:
        # Fallback if LLM fails
        fallback = (
            f"[RAG fallback] Retrieved {len(retrieved_texts)} snippet(s) "
            f"but LLM call failed: {e}"
        )
        return {
            "retrieved_chunks": retrieved_texts,
            "reply": fallback,
        }



def design_explainer_node(state: GraphState) -> GraphState:
    """
    Design explainer node.

    - Assumes RAG has already run (retrieved_chunks is filled).
    - Uses a system-design-style prompt to explain the architecture.
    """
    user_input = state.get("user_input", "")
    retrieved_texts = state.get("retrieved_chunks", [])

    if not user_input:
        return {"reply": "I did not receive any input.", "retrieved_chunks": retrieved_texts}

    if not settings.use_llm or not settings.groq_api_key:
        # Fallback to normal RAG-style reply if LLM is disabled
        return code_qa_node(state)

    try:
        llm_answer = explain_design_with_context(user_input, retrieved_texts)
        return {
            "retrieved_chunks": retrieved_texts,
            "reply": llm_answer,
        }
    except Exception as e:
        fallback = (
            f"[Design explainer fallback] Retrieved {len(retrieved_texts)} snippet(s) "
            f"but LLM call failed: {e}"
        )
        return {
            "retrieved_chunks": retrieved_texts,
            "reply": fallback,
        }






def build_graph():
    """
    Build and compile a LangGraph graph:

    START -> file_reader_node -> planner_node -> ingestion_node -> code_qa_node -> END
    """
    builder = StateGraph(GraphState)

    builder.add_node("file_reader_node", file_reader_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("ingestion_node", ingestion_node)
    builder.add_node("code_qa_node", code_qa_node)
    builder.add_node("design_explainer_node", design_explainer_node)  # NEW

    # Single, linear flow (no parallel START edges)
    builder.add_edge(START, "file_reader_node")
    builder.add_edge("file_reader_node", "planner_node")
    builder.add_edge("planner_node", "ingestion_node")
    builder.add_edge("ingestion_node", "code_qa_node")
    builder.add_edge("code_qa_node", "design_explainer_node")         # NEW
    builder.add_edge("design_explainer_node", END)                    # NEW
    
    graph = builder.compile()
    return graph



graph_app = build_graph()




# Planner still sets message_type (we’ll use it later).
# code_qa_node uses the “fake RAG” components to retrieve snippets and build a reply.

# Now:
# Ingestion uses embed_chunks → real sentence‑transformers embeddings.
# Query uses embed_text → real embeddings.
# Similarity search is still naive but now based on a meaningful vector space.

#Now:
# Retrieval still uses your local vector store + sentence‑transformers.
# Final reply is generated by the LLM, given the retrieved context.

# Now we have truly have both:
# When USE_LLM=false or OPENAI_API_KEY is empty:
# RAG‑only mode, fully local.
# When USE_LLM=true and a valid key is set:
# RAG + online LLM answers.


# So the graph path is now:
# START → planner_node → ingestion_node → code_qa_node → END.

# This means:
# Every request:
# Planner runs (still just classifies).
# Ingestion ensures vector store is built from sample_data.
# Code‑QA uses that store to answer.

# Later, planner will decide whether ingestion is needed or not.


