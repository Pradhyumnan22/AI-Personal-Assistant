"""Notes CRUD and indexing endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import DatabaseSession
from app.db.repositories import NoteRepository
from app.llm import OpenAIClient
from app.rag import LocalRetriever
from app.schemas.notes import NoteResponse, NoteWrite
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/v1/notes", dependencies=[Depends(verify_api_key)]
)


@router.get("", response_model=list[NoteResponse])
def list_notes(session: DatabaseSession):
    return NoteRepository(session).list()


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteWrite, session: DatabaseSession):
    return NoteRepository(session).create(payload.title, payload.content)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: str, payload: NoteWrite, session: DatabaseSession):
    repository = NoteRepository(session)
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return repository.update(note, payload.title, payload.content)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, session: DatabaseSession) -> Response:
    repository = NoteRepository(session)
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    repository.delete(note)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{note_id}/index", status_code=status.HTTP_204_NO_CONTENT)
async def index_note(note_id: str, session: DatabaseSession) -> Response:
    note = NoteRepository(session).get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    try:
        await LocalRetriever(session, OpenAIClient()).index_note(note.id, note.content)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
