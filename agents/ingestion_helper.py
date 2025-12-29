from typing import Optional

from rag.chunking import simple_line_chunker
from rag.embeddings import embed_chunks, embed_text
from rag.vectorstore import InMemoryVectorStore, StoredChunk

# Global in-memory vector store for Phase 3 demo
VECTOR_STORE: Optional[InMemoryVectorStore] = None


def init_vector_store_with_sample_text() -> InMemoryVectorStore:
    """
    Initialize the global vector store with some sample text.

    Later this will be replaced by real repo ingestion.
    """
    global VECTOR_STORE

    sample_text = """
    DevGraph Copilot is a multi-agent system for understanding GitHub repositories.
    It uses FastAPI as the backend framework and LangGraph to orchestrate agents.
    Agents can perform tasks like planning, ingestion, data quality checks, and code Q&A.
    In the future, MCP tools will allow integration with external services.
    This sample text is used only for the Phase 3 fake RAG demo.
    """

    chunks = simple_line_chunker(sample_text)
    embeddings = embed_chunks(chunks)

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)

    VECTOR_STORE = store
    return store


def get_vector_store() -> InMemoryVectorStore:
    """
    Returns the global vector store, initializing it if needed.
    """
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = init_vector_store_with_sample_text()
    return VECTOR_STORE


# This gives you:
# A global VECTOR_STORE initialized with some sample text at first use.