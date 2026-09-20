"""FastAPI dependency providers."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chat import ChatService

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_chat_service(session: DatabaseSession) -> ChatService:
    try:
        return ChatService(session)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
