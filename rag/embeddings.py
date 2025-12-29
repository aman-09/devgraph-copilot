from typing import List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings


# Global embedding model instance (lazy-initialized)
_embedding_model: Optional[HuggingFaceEmbeddings] = None


def get_local_embedding_model() -> HuggingFaceEmbeddings:
    """
    Returns a sentence-transformers-based embedding model
    that runs locally via HuggingFace.

    Model: all-MiniLM-L6-v2 (small, fast, good for demos).
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embedding_model


def embed_text(text: str) -> List[float]:
    """
    Embed a single text string into a vector.
    """
    model = get_local_embedding_model()
    # embed_query returns List[float]
    return model.embed_query(text)


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Embed a list of chunks into vectors.
    """
    model = get_local_embedding_model()
    return model.embed_documents(chunks)


# Notes:
# get_local_embedding_model() loads all-MiniLM-L6-v2 once and reuses it.
# ​embed_text is the replacement for dummy_embedding.
# embed_chunks now uses the real model, but function name stays the same so ingestion_helper works with no change.