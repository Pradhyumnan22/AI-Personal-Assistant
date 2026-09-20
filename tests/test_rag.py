"""Unit tests for local RAG utilities."""

import pytest

from app.rag.retriever import chunk_text, cosine_similarity


def test_chunk_text_preserves_overlap():
    chunks = chunk_text("a" * 1000, size=500, overlap=100)
    assert len(chunks) == 3
    assert chunks[0][-100:] == chunks[1][:100]


def test_cosine_similarity():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
