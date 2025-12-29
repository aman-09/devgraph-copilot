from langgraph.graph import StateGraph, START, END

from .graph_state import GraphState
from .ingestion_helper import get_vector_store
from rag.embeddings import embed_text


def planner_node(state: GraphState) -> GraphState:
    """
    Very simple 'planner' for now.

    It only classifies the message type.
    Later it can decide which agent to call (code_qa, docs, etc.).
    """
    user_input = state.get("user_input", "")
    msg_type = "question" if user_input.strip().endswith("?") else "statement"
    return {"message_type": msg_type}


def code_qa_node(state: GraphState) -> GraphState:
    """
    Fake Code-QA node using in-memory vector store and dummy embeddings.

    - Embeds the user_input.
    - Searches the vector store.
    - Returns the top chunks as 'retrieved_chunks' and a simple reply.
    """
    user_input = state.get("user_input", "")
    if not user_input:
        return {"reply": "I did not receive any input.", "retrieved_chunks": []}

    # 1) Get vector store (init if needed)
    store = get_vector_store()

    # 2) Create embedding for query
    query_emb = embed_text(user_input)

    # 3) Search in store
    top_chunks = store.search(query_emb, top_k=3)

    retrieved_texts = [c.text for c in top_chunks]

    # 4) Build a simple reply: echo + show retrieved snippets
    joined_snippets = " | ".join(retrieved_texts) if retrieved_texts else "No relevant text found."

    reply = (
        f"[Fake RAG] You asked: '{user_input}'. "
        f"Top snippets from knowledge base: {joined_snippets}"
    )

    return {
        "retrieved_chunks": retrieved_texts,
        "reply": reply,
    }


def build_graph():
    """
    Build and compile a LangGraph graph:

    START -> planner_node -> code_qa_node -> END
    """
    builder = StateGraph(GraphState)

    builder.add_node("planner_node", planner_node)
    builder.add_node("code_qa_node", code_qa_node)

    builder.add_edge(START, "planner_node")
    builder.add_edge("planner_node", "code_qa_node")
    builder.add_edge("code_qa_node", END)

    graph = builder.compile()
    return graph


graph_app = build_graph()




# Planner still sets message_type (we’ll use it later).
# code_qa_node uses the “fake RAG” components to retrieve snippets and build a reply.

# Now:
# Ingestion uses embed_chunks → real sentence‑transformers embeddings.
# Query uses embed_text → real embeddings.
# Similarity search is still naive but now based on a meaningful vector space.
