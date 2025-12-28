from typing import List
from dataclasses import dataclass


@dataclass
class StoredChunk:
    text: str
    embedding: List[float]


class InMemoryVectorStore:
    """
    Phase 3 placeholder:
    Stores chunks + fake embeddings in memory and does a very naive search.
    """

    def __init__(self):
        self._store: List[StoredChunk] = []

    def add(self, chunks: List[str], embeddings: List[List[float]]) -> None:
        for text, emb in zip(chunks, embeddings):
            self._store.append(StoredChunk(text=text, embedding=emb))

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[StoredChunk]:
        if not self._store:
            return []

        def score(chunk: StoredChunk) -> float:
            # naive: use first dimension difference
            return -abs(chunk.embedding[0] - query_embedding[0])

        sorted_chunks = sorted(self._store, key=score)
        return sorted_chunks[:top_k]
