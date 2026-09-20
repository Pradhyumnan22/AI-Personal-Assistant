"""Notes CRUD and indexing endpoints."""

from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pypdf import PdfReader

from app.api.dependencies import DatabaseSession, get_llm_client
from app.core.security import verify_api_key
from app.db.repositories import NoteRepository
from app.llm import LLMClient
from app.rag import LocalRetriever
from app.schemas.notes import NoteResponse, NoteWrite

router = APIRouter(
    prefix="/api/v1/notes", dependencies=[Depends(verify_api_key)]
)
documents_router = APIRouter(
    prefix="/api/v1/documents", dependencies=[Depends(verify_api_key)]
)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
LLMDependency = Annotated[LLMClient, Depends(get_llm_client)]


@router.get("", response_model=list[NoteResponse])
def list_notes(session: DatabaseSession):
    return NoteRepository(session).list()


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteWrite, session: DatabaseSession, llm: LLMDependency
):
    note = NoteRepository(session).create(payload.title, payload.content)
    await LocalRetriever(session, llm).index_note(note.id, note.content)
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str, payload: NoteWrite, session: DatabaseSession, llm: LLMDependency
):
    repository = NoteRepository(session)
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note = repository.update(note, payload.title, payload.content)
    await LocalRetriever(session, llm).index_note(note.id, note.content)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, session: DatabaseSession) -> Response:
    repository = NoteRepository(session)
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    repository.delete(note)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{note_id}/index", status_code=status.HTTP_204_NO_CONTENT)
async def index_note(
    note_id: str, session: DatabaseSession, llm: LLMDependency
) -> Response:
    note = NoteRepository(session).get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await LocalRetriever(session, llm).index_note(note.id, note.content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@documents_router.post(
    "", response_model=NoteResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    session: DatabaseSession,
    llm: LLMDependency,
    file: UploadFile = File(...),
):
    filename = file.filename or "Uploaded document"
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=415, detail="Only PDF, TXT, and Markdown files are supported"
        )
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit")
    try:
        if suffix == ".pdf":
            content = "\n\n".join(
                page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages
            )
        else:
            content = data.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Unable to read document") from exc
    if not content.strip():
        raise HTTPException(status_code=422, detail="Document contains no readable text")
    note = NoteRepository(session).create(Path(filename).stem, content)
    await LocalRetriever(session, llm).index_note(note.id, note.content)
    return note
