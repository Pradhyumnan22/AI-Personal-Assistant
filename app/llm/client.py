"""LLM provider boundary."""

import json
from dataclasses import dataclass
from typing import Protocol

from openai import AsyncOpenAI

from app.core.config import settings


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict


@dataclass(frozen=True)
class ToolDecision:
    content: str
    calls: list[ToolCall]


class LLMClient(Protocol):
    async def complete(self, messages: list[dict[str, str]]) -> str: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def complete_with_tools(
        self, messages: list[dict[str, str]], tools: list[dict]
    ) -> ToolDecision: ...


class OpenAIClient:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def complete(self, messages: list[dict[str, str]]) -> str:
        response = await self.client.chat.completions.create(
            model=settings.openai_model, messages=messages  # type: ignore[arg-type]
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=settings.embedding_model, input=texts
        )
        return [item.embedding for item in response.data]

    async def complete_with_tools(
        self, messages: list[dict[str, str]], tools: list[dict]
    ) -> ToolDecision:
        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,  # type: ignore[arg-type]
            tools=tools,  # type: ignore[arg-type]
            tool_choice="auto",
        )
        message = response.choices[0].message
        calls = [
            ToolCall(
                name=call.function.name,
                arguments=json.loads(call.function.arguments or "{}"),
            )
            for call in (message.tool_calls or [])
        ]
        return ToolDecision(content=message.content or "", calls=calls)
