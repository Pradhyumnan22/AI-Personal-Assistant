"""Tests for task tool execution."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.llm import ToolCall
from app.tools import TaskToolbox


def test_task_toolbox_creates_and_lists_tasks():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        toolbox = TaskToolbox(session)
        result = toolbox.execute(
            ToolCall(
                name="create_task",
                arguments={"title": "Review PR", "due_at": None},
            )
        )
        listed = toolbox.execute(
            ToolCall(name="list_tasks", arguments={"include_completed": True})
        )

    assert "Created task 'Review PR'" in result
    assert "Review PR" in listed
