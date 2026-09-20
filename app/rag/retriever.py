"""Small replaceable local embedding retriever."""

import json
import math

from sqlalchemy.orm import Session

from app.db.repositories import NoteRepository
from app.llm import LLMClient


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks, start = [], 0
    while start < len(clean):
        chunks.append(clean[start : start + size])
        start += size - overlap
    return chunks


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    magnitude = math.sqrt(sum(a * a for a in left)) * math.sqrt(
        sum(b * b for b in right)
    )
    return dot / magnitude if magnitude else 0.0


class LocalRetriever:
    def __init__(self, session: Session, llm: LLMClient):
        self.repository = NoteRepository(session)
        self.llm = llm

    async def index_note(self, note_id: str, content: str) -> None:
        chunks = chunk_text(content)
        embeddings = await self.llm.embed(chunks) if chunks else []
        self.repository.replace_chunks(
            note_id,
            [(chunk, json.dumps(embedding)) for chunk, embedding in zip(chunks, embeddings)],
        )

    async def search(self, query: str, limit: int = 3) -> list[str]:
        chunks = [chunk for chunk in self.repository.chunks() if chunk.embedding]
        if not chunks:
            return []
        query_vector = (await self.llm.embed([query]))[0]
        ranked = sorted(
            chunks,
            key=lambda item: cosine_similarity(
                query_vector, json.loads(item.embedding or "[]")
            ),
            reverse=True,
        )
        return [chunk.content for chunk in ranked[:limit]]
