"""Repository layer for persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, DocumentChunk, Message, Note


class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str = "New conversation") -> Conversation:
        item = Conversation(title=title)
        self.session.add(item)
        self.session.commit()
        return item

    def get(self, conversation_id: str) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    def list(self) -> list[Conversation]:
        statement = select(Conversation).order_by(Conversation.updated_at.desc())
        return list(self.session.scalars(statement))

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        message = Message(
            conversation_id=conversation_id, role=role, content=content
        )
        self.session.add(message)
        self.session.commit()
        return message

    def messages(self, conversation_id: str, limit: int = 20) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(list(self.session.scalars(statement))))


class NoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, content: str) -> Note:
        note = Note(title=title, content=content)
        self.session.add(note)
        self.session.commit()
        return note

    def list(self) -> list[Note]:
        return list(self.session.scalars(select(Note).order_by(Note.updated_at.desc())))

    def get(self, note_id: str) -> Note | None:
        return self.session.get(Note, note_id)

    def update(self, note: Note, title: str, content: str) -> Note:
        note.title, note.content = title, content
        self.session.commit()
        return note

    def delete(self, note: Note) -> None:
        self.session.delete(note)
        self.session.commit()

    def replace_chunks(self, note_id: str, chunks: list[tuple[str, str | None]]) -> None:
        current = self.session.scalars(
            select(DocumentChunk).where(DocumentChunk.note_id == note_id)
        )
        for chunk in current:
            self.session.delete(chunk)
        self.session.add_all(
            DocumentChunk(note_id=note_id, content=text, embedding=embedding)
            for text, embedding in chunks
        )
        self.session.commit()

    def chunks(self) -> list[DocumentChunk]:
        return list(self.session.scalars(select(DocumentChunk)))
