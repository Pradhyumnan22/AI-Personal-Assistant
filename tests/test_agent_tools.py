"""Agent workflow tool-calling test."""

import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.agents import build_assistant_graph
from app.db.models import Base
from app.llm import ToolCall, ToolDecision
from app.tools import TaskToolbox


class ToolCallingLLM:
    async def complete_with_tools(self, messages, tools):
        return ToolDecision(
            content="",
            calls=[
                ToolCall(
                    name="create_task",
                    arguments={"title": "Finish report", "due_at": None},
                )
            ],
        )

    async def complete(self, messages):
        return "I created the task."

    async def embed(self, texts):
        return [[1.0] for _ in texts]


def test_agent_executes_task_tool():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        toolbox = TaskToolbox(session)
        graph = build_assistant_graph(ToolCallingLLM(), toolbox)
        result = asyncio.run(
            graph.ainvoke(
                {"messages": [{"role": "user", "content": "Create a report task"}]}
            )
        )
        tasks = toolbox.repository.list()

    assert result["response"] == "I created the task."
    assert tasks[0].title == "Finish report"
