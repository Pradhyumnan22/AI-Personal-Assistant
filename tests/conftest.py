"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_llm_client
from app.db.models import Base
from app.db.session import get_db
from app.main import app


class FakeLLM:
    async def complete(self, messages):
        return "Test response"

    async def embed(self, texts):
        return [[float(len(text)), 1.0] for text in texts]


@pytest.fixture
def client() -> TestClient:
    """HTTP client bound to the FastAPI application."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def test_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_llm_client] = lambda: FakeLLM()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
