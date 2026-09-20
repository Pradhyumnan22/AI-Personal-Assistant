"""Task API contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    due_at: datetime | None = None


class TaskUpdate(TaskCreate):
    completed: bool = False


class TaskResponse(TaskUpdate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
