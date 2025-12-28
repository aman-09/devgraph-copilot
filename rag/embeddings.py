from typing import List
import math


def dummy_embedding(text: str) -> List[float]:
    """
    Phase 3 placeholder:
    Returns a tiny 'embedding' based on text length.

    This is just to keep the code wiring simple until we plug
    in a real embedding model.
    """
    length = len(text)
    # Fake 3-dim vector derived from length
    return [length, math.sqrt(length + 1), length % 7]


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    return [dummy_embedding(chunk) for chunk in chunks]
