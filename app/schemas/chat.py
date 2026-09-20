"""Chat and conversation API contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    conversation_id: str | None = None


class SourceResponse(BaseModel):
    note_id: str
    title: str
    excerpt: str


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    sources: list[SourceResponse] = Field(default_factory=list)


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
