"""Minimal LangGraph assistant workflow."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.llm import LLMClient

SYSTEM_PROMPT = (
    "You are a concise, reliable personal assistant. Use supplied context when "
    "it is relevant. Never claim to have completed actions you did not perform."
)


class AgentState(TypedDict):
    messages: list[dict[str, str]]
    response: str


def build_assistant_graph(llm: LLMClient):
    async def respond(state: AgentState) -> dict[str, str]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]]
        return {"response": await llm.complete(messages)}

    graph = StateGraph(AgentState)
    graph.add_node("respond", respond)
    graph.add_edge(START, "respond")
    graph.add_edge("respond", END)
    return graph.compile()
