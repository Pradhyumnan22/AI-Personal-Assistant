"""Minimal LangGraph assistant workflow."""

from typing import Protocol, TypedDict
from datetime import datetime, timezone

from langgraph.graph import END, START, StateGraph

from app.llm import LLMClient, ToolCall

SYSTEM_PROMPT = (
    "You are a concise, reliable personal assistant. Use supplied context when "
    "it is relevant. Never claim to have completed actions you did not perform."
)


class AgentState(TypedDict, total=False):
    messages: list[dict[str, str]]
    response: str
    tool_calls: list[ToolCall]
    tool_results: list[str]


class AgentToolbox(Protocol):
    definitions: list[dict]

    def execute(self, call: ToolCall) -> str: ...


def build_assistant_graph(llm: LLMClient, toolbox: AgentToolbox | None = None):
    def system_message() -> dict[str, str]:
        return {
            "role": "system",
            "content": (
                f"{SYSTEM_PROMPT}\nCurrent UTC time: "
                f"{datetime.now(timezone.utc).isoformat()}. "
                "Use task tools whenever the user asks to create, list, complete, "
                "or delete tasks or reminders. Use calendar tools for requests about "
                "Google Calendar events; if Calendar is disconnected, explain that "
                "the user must connect it from the Calendar page."
            ),
        }

    async def decide(state: AgentState) -> dict:
        messages = [system_message(), *state["messages"]]
        if toolbox is None:
            return {"response": await llm.complete(messages), "tool_calls": []}
        decision = await llm.complete_with_tools(messages, toolbox.definitions)
        return {"response": decision.content, "tool_calls": decision.calls}

    def route_decision(state: AgentState) -> str:
        return "tools" if state.get("tool_calls") else END

    async def execute_tools(state: AgentState) -> dict[str, list[str]]:
        assert toolbox is not None
        return {
            "tool_results": [
                toolbox.execute(call) for call in state.get("tool_calls", [])
            ]
        }

    async def summarize_tools(state: AgentState) -> dict[str, str]:
        messages = [
            system_message(),
            *state["messages"],
            {
                "role": "system",
                "content": "Tool results:\n" + "\n".join(state["tool_results"]),
            },
        ]
        return {"response": await llm.complete(messages)}

    graph = StateGraph(AgentState)
    graph.add_node("decide", decide)
    graph.add_node("tools", execute_tools)
    graph.add_node("summarize", summarize_tools)
    graph.add_edge(START, "decide")
    graph.add_conditional_edges("decide", route_decision, {"tools": "tools", END: END})
    graph.add_edge("tools", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()
