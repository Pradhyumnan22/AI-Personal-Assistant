"""Chat and conversation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import DatabaseSession, get_chat_service
from app.db.repositories import ConversationRepository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationPinRequest,
    ConversationResponse,
    MessageResponse,
    SourceResponse,
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
        conversation_id, answer, sources = await service.chat(
            request.message, request.conversation_id
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return ChatResponse(
        conversation_id=conversation_id,
        message=answer,
        sources=[
            SourceResponse(
                note_id=source.note_id,
                title=source.title,
                excerpt=source.content[:240],
            )
            for source in sources
        ],
    )


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


@router.patch(
    "/conversations/{conversation_id}/pin",
    response_model=ConversationResponse,
)
def pin_conversation(
    conversation_id: str,
    payload: ConversationPinRequest,
    session: DatabaseSession,
):
    repository = ConversationRepository(session)
    conversation = repository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return repository.set_pinned(conversation, payload.pinned)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(conversation_id: str, session: DatabaseSession) -> Response:
    repository = ConversationRepository(session)
    conversation = repository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    repository.delete(conversation)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
