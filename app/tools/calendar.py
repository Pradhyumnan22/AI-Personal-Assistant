"""Google Calendar tools exposed to the agent."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.integrations.google_calendar import (
    CalendarConfigurationError,
    GoogleCalendarService,
)
from app.llm import ToolCall

CALENDAR_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_calendar_events",
            "description": "List upcoming events from the user's connected Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20}
                },
                "required": ["limit"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create an event in the user's connected Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start": {
                        "type": "string",
                        "description": "ISO 8601 date-time including timezone.",
                    },
                    "end": {
                        "type": ["string", "null"],
                        "description": "Optional ISO 8601 end date-time.",
                    },
                    "description": {"type": ["string", "null"]},
                },
                "required": ["title", "start", "end", "description"],
                "additionalProperties": False,
            },
        },
    },
]


class CalendarToolbox:
    definitions = CALENDAR_TOOL_DEFINITIONS

    def __init__(self, session: Session):
        self.service = GoogleCalendarService(session)

    def execute(self, call: ToolCall) -> str:
        try:
            if call.name == "list_calendar_events":
                events = self.service.list_events(int(call.arguments.get("limit", 10)))
                if not events:
                    return "There are no upcoming calendar events."
                return "\n".join(
                    f"- {event['title']} | {event['start']} to {event['end']}"
                    for event in events
                )
            if call.name == "create_calendar_event":
                event = self.service.create_event(
                    title=call.arguments["title"],
                    start=datetime.fromisoformat(call.arguments["start"]),
                    end=datetime.fromisoformat(call.arguments["end"])
                    if call.arguments.get("end")
                    else None,
                    description=call.arguments.get("description"),
                )
                return (
                    f"Created calendar event '{event['title']}' starting "
                    f"{event['start']}."
                )
        except CalendarConfigurationError:
            return (
                "Google Calendar is not connected. Ask the user to connect it "
                "from the Calendar page."
            )
        return f"Unknown calendar tool: {call.name}."
