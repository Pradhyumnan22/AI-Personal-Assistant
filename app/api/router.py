"""Top-level API router that aggregates route modules."""

from fastapi import APIRouter

from app.api.routes import chat, health, notes, root, tasks

api_router = APIRouter()
api_router.include_router(root.router, tags=["root"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(notes.router, tags=["notes"])
api_router.include_router(notes.documents_router, tags=["documents"])
api_router.include_router(tasks.router, tags=["tasks"])
