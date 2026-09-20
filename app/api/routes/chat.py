"""Chat and conversation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import DatabaseSession, get_chat_service
from app.db.repositories import ConversationRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services.chat import ChatService
from app.core.security import verify_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    try:
        conversation_id, answer = await service.chat(
            request.message, request.conversation_id
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return ChatResponse(conversation_id=conversation_id, message=answer)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(session: DatabaseSession):
    return ConversationRepository(session).list()


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(conversation_id: str, session: DatabaseSession):
    repository = ConversationRepository(session)
    if repository.get(conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return repository.messages(conversation_id, limit=100)
