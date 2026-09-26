"""Combined tool registry for the assistant agent."""

from sqlalchemy.orm import Session

from app.llm import ToolCall
from app.tools.calendar import CalendarToolbox
from app.tools.tasks import TaskToolbox


class AssistantToolbox:
    def __init__(self, session: Session):
        self.tasks = TaskToolbox(session)
        self.calendar = CalendarToolbox(session)
        self.definitions = [*self.tasks.definitions, *self.calendar.definitions]

    def execute(self, call: ToolCall) -> str:
        if call.name in {
            "create_task",
            "list_tasks",
            "complete_task",
            "delete_task",
        }:
            return self.tasks.execute(call)
        return self.calendar.execute(call)
