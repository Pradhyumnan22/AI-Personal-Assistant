"""LLM provider boundary."""

from typing import Protocol

from openai import AsyncOpenAI

from app.core.config import settings


class LLMClient(Protocol):
    async def complete(self, messages: list[dict[str, str]]) -> str: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


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
