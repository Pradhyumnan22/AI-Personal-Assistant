"""Notes API contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteWrite(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100_000)


class NoteResponse(NoteWrite):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
