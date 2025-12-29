from typing import Optional, List
from pathlib import Path

from rag.chunking import simple_line_chunker
from rag.embeddings import embed_chunks, embed_text
from rag.vectorstore import InMemoryVectorStore, StoredChunk

# Global in-memory vector store
VECTOR_STORE: Optional[InMemoryVectorStore] = None

# Simple flag so we know if ingestion ran at least once
INGESTION_RAN: bool = False


def init_vector_store_with_sample_text() -> InMemoryVectorStore:
    """
    Initialize the vector store with a hardcoded sample text.
    (Kept for fallback / testing.)
    """
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
    return store


def ingest_folder(folder_path: Path) -> InMemoryVectorStore:
    """
    Read all .txt files in the given folder, chunk + embed them,
    and populate a new InMemoryVectorStore.
    """
    texts: List[str] = []

    for path in folder_path.rglob("*.txt"):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            texts.append(content)
        except Exception:
            # Skip unreadable files
            continue

    if not texts:
        # If no files, fallback to hardcoded sample text
        return init_vector_store_with_sample_text()

    # Combine all text files into one big string for now
    full_text = "\n\n".join(texts)

    chunks = simple_line_chunker(full_text)
    embeddings = embed_chunks(chunks)

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)
    return store


def init_or_refresh_vector_store() -> InMemoryVectorStore:
    """
    Initialize or refresh the global VECTOR_STORE using local sample_data folder.
    """
    global VECTOR_STORE, INGESTION_RAN

    base_dir = Path(__file__).resolve().parent.parent  # project root-ish
    data_dir = base_dir / "sample_data"

    if not data_dir.exists():
        # If folder does not exist, fallback to sample text
        store = init_vector_store_with_sample_text()
    else:
        store = ingest_folder(data_dir)

    VECTOR_STORE = store
    INGESTION_RAN = True
    return store


def get_vector_store() -> InMemoryVectorStore:
    """
    Returns the global vector store, initializing it if needed.
    """
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = init_or_refresh_vector_store()
    return VECTOR_STORE



# This gives you:
# A global VECTOR_STORE initialized with some sample text at first use.

# init_or_refresh_vector_store() reads all .txt files under sample_data/ and builds the store.
# If no files, falls back to the old sample text.