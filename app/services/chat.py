"""Chat application service."""

from sqlalchemy.orm import Session

from app.agents import build_assistant_graph
from app.core.config import settings
from app.db.repositories import ConversationRepository
from app.llm import LLMClient, OpenAIClient
from app.rag import LocalRetriever


class ChatService:
    def __init__(self, session: Session, llm: LLMClient | None = None):
        self.repository = ConversationRepository(session)
        self.llm = llm or OpenAIClient()
        self.graph = build_assistant_graph(self.llm)
        self.retriever = LocalRetriever(session, self.llm)

    async def chat(self, content: str, conversation_id: str | None = None):
        conversation = (
            self.repository.get(conversation_id) if conversation_id else None
        )
        if conversation_id and conversation is None:
            raise LookupError("Conversation not found")
        if conversation is None:
            conversation = self.repository.create(title=content[:80])

        self.repository.add_message(conversation.id, "user", content)
        history = self.repository.messages(
            conversation.id, limit=settings.max_context_messages
        )
        context = await self.retriever.search(content)
        messages = [
            {"role": message.role, "content": message.content} for message in history
        ]
        if context:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": "Relevant saved knowledge:\n\n"
                    + "\n\n---\n\n".join(
                        f"[Source: {item.title}]\n{item.content}" for item in context
                    ),
                },
            )
        result = await self.graph.ainvoke(
            {
                "messages": messages,
                "response": "",
            }
        )
        answer = result["response"]
        self.repository.add_message(conversation.id, "assistant", answer)
        return conversation.id, answer, context
