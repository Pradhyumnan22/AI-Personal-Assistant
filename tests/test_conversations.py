"""Conversation pinning and deletion tests."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.db.repositories import ConversationRepository


def test_pinned_conversations_sort_first_and_can_be_deleted():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repository = ConversationRepository(session)
        first = repository.create("First")
        pinned = repository.create("Pinned")
        repository.set_pinned(pinned, True)

        assert repository.list()[0].id == pinned.id
        assert repository.list()[0].pinned is True

        repository.delete(first)
        assert repository.get(first.id) is None
