"""Task tools exposed to the assistant workflow."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.repositories import TaskRepository
from app.llm import ToolCall


TASK_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task or reminder for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "due_at": {
                        "type": ["string", "null"],
                        "description": "ISO 8601 date-time, or null when no due date is given.",
                    },
                },
                "required": ["title", "due_at"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks, including IDs and due dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_completed": {"type": "boolean"},
                },
                "required": ["include_completed"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task complete using its task ID.",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task using its task ID.",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
                "additionalProperties": False,
            },
        },
    },
]


class TaskToolbox:
    definitions = TASK_TOOL_DEFINITIONS

    def __init__(self, session: Session):
        self.repository = TaskRepository(session)

    def execute(self, call: ToolCall) -> str:
        if call.name == "create_task":
            due_value = call.arguments.get("due_at")
            due_at = datetime.fromisoformat(due_value) if due_value else None
            task = self.repository.create(call.arguments["title"], due_at)
            return f"Created task '{task.title}' with ID {task.id}."
        if call.name == "list_tasks":
            tasks = self.repository.list(
                bool(call.arguments.get("include_completed", True))
            )
            if not tasks:
                return "There are no matching tasks."
            return "\n".join(
                f"- {task.title} | ID: {task.id} | due: "
                f"{task.due_at.isoformat() if task.due_at else 'none'} | "
                f"completed: {task.completed}"
                for task in tasks
            )
        task_id = str(call.arguments.get("task_id", ""))
        task = self.repository.get(task_id)
        if task is None:
            return f"Task {task_id} was not found."
        if call.name == "complete_task":
            self.repository.complete(task)
            return f"Completed task '{task.title}'."
        if call.name == "delete_task":
            title = task.title
            self.repository.delete(task)
            return f"Deleted task '{title}'."
        return f"Unknown tool: {call.name}."
