"""Calendar tool behavior without an OAuth connection."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.llm import ToolCall
from app.tools.calendar import CalendarToolbox


def test_calendar_tool_requests_connection_when_disconnected():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        result = CalendarToolbox(session).execute(
            ToolCall(name="list_calendar_events", arguments={"limit": 5})
        )

    assert "not connected" in result
