from typing import Optional, List
from pathlib import Path

from rag.chunking import simple_line_chunker
from rag.embeddings import embed_chunks, embed_text
from rag.vectorstore import InMemoryVectorStore, StoredChunk

ALLOWED_EXTS = {".py", ".md", ".txt"}  # start small
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".idea", ".mypy_cache"}
MAX_FILES = 500  # hard cap for now


# Global in-memory vector store
VECTOR_STORE: Optional[InMemoryVectorStore] = None

# Simple flag so we know if ingestion ran at least once
INGESTION_RAN: bool = False

# Local repo root to ingest
REPO_ROOT = Path(r"C:\Users\amanb\Downloads\devgraph-copilot")


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


import logging

logger = logging.getLogger(__name__)


def ingest_folder(folder_path: Path) -> InMemoryVectorStore:
    """
    Read code/docs in the given folder, chunk + embed them,
    and populate a new InMemoryVectorStore.
    """
    texts: List[str] = []
    file_count = 0

    logger.info("Ingestion: scanning folder %s", folder_path)

    for path in folder_path.rglob("*"):
        if not path.is_file():
            continue

        # Skip unwanted directories like .git, .venv, caches
        try:
            rel = path.relative_to(folder_path)
        except ValueError:
            continue
        parts = rel.parts
        if parts and parts[0] in SKIP_DIRS:
            continue

        # Restrict to certain extensions
        if path.suffix.lower() not in ALLOWED_EXTS:
            continue

        file_count += 1
        logger.info("Ingestion: using file #%d: %s", file_count, path)

        if file_count > MAX_FILES:
            logger.info("Ingestion: reached MAX_FILES=%d, stopping scan.", MAX_FILES)
            break

        if file_count % 20 == 0:
            logger.info("Ingestion: processed %d files so far (last: %s)", file_count, path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            texts.append(content)
        except Exception as e:
            logger.warning("Ingestion: failed to read %s: %s", path, e)
            continue

    logger.info("Ingestion: finished scanning. Used files=%d", file_count)

    if not texts:
        logger.info("Ingestion: no files found, falling back to sample text.")
        return init_vector_store_with_sample_text()

    full_text = "\n\n".join(texts)
    logger.info("Ingestion: combined text length=%d chars", len(full_text))

    chunks = simple_line_chunker(full_text)
    logger.info("Ingestion: created %d chunks, starting embeddings...", len(chunks))

    embeddings = embed_chunks(chunks)
    logger.info("Ingestion: embeddings computed for %d chunks, building vector store...", len(chunks))

    store = InMemoryVectorStore()
    store.add(chunks, embeddings)
    logger.info("Ingestion: vector store built successfully.")
    return store


def init_or_refresh_vector_store() -> InMemoryVectorStore:
    """
    Initialize or refresh the global VECTOR_STORE using local repo (or fallback).
    """
    global VECTOR_STORE, INGESTION_RAN

    logger.info("init_or_refresh_vector_store: starting ingestion...")

    if REPO_ROOT.exists():
        logger.info("init_or_refresh_vector_store: using REPO_ROOT=%s", REPO_ROOT)
        store = ingest_folder(REPO_ROOT)
    else:
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "sample_data"
        if data_dir.exists():
            logger.info("init_or_refresh_vector_store: REPO_ROOT missing, using sample_data=%s", data_dir)
            store = ingest_folder(data_dir)
        else:
            logger.info("init_or_refresh_vector_store: no repo/sample_data, using sample text.")
            store = init_vector_store_with_sample_text()

    VECTOR_STORE = store
    INGESTION_RAN = True
    logger.info("init_or_refresh_vector_store: done.")
    return store


def get_vector_store() -> InMemoryVectorStore:
    """
    Returns the global vector store, initializing it if needed.
    """
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = init_or_refresh_vector_store()
    return VECTOR_STORE
