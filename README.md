# AI Personal Assistant

A full-stack AI engineering portfolio project using FastAPI, LangGraph, OpenAI,
React, SQLite, and a small replaceable RAG layer.

## Capabilities

- Persistent conversations and messages
- Minimal LangGraph workflow backed by OpenAI
- Notes CRUD with automatic semantic indexing
- PDF, text, and Markdown document uploads
- Retrieved source citations in chat responses
- Persistent tasks and reminders with LangGraph tool calling
- Responsive React chat client
- Optional API-key protection, request IDs, tests, CI, and deployment manifests

## Structure

```text
app/             FastAPI backend and application layers
  agents/        LangGraph workflow
  api/           Versioned routes and dependencies
  db/            SQLAlchemy models, sessions, repositories
  llm/           OpenAI provider boundary
  rag/           Chunking, indexing, local vector retrieval
  services/      Application use cases
frontend/        Vite + React + TypeScript client
migrations/      Alembic database migrations
tests/           Backend unit and integration tests
```

## Local setup

Requirements: Python 3.11+, Node.js 22+, and an OpenAI API key.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set `OPENAI_API_KEY` in `.env`, then initialize and run the backend:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal, run the frontend:

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173. API docs are at http://127.0.0.1:8000/docs.

## API

- `POST /api/v1/chat`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{id}/messages`
- `GET|POST /api/v1/notes`
- `PUT|DELETE /api/v1/notes/{id}`
- `POST /api/v1/notes/{id}/index`
- `POST /api/v1/documents` (PDF, TXT, or Markdown; 10 MB maximum)
- `GET|POST /api/v1/tasks`
- `PUT|DELETE /api/v1/tasks/{id}`
- `POST /api/v1/tasks/{id}/complete`
- `GET /health`

Notes and uploaded documents are indexed automatically. The explicit `/index`
endpoint can be used to rebuild an existing note's embeddings.
If `API_KEY` is configured, send it as the `X-API-Key` header.

## Quality checks

```powershell
pytest
cd frontend
npm run build
```

GitHub Actions runs both checks. Vercel configuration lives in `frontend/`;
`render.yaml` configures the API. Use managed PostgreSQL on Render because its
default filesystem is ephemeral; set `DATABASE_URL` to the managed connection
string. SQLite is intended for local development.

## Database migrations

After changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Secrets belong in `.env` or deployment environment variables and must never be
committed.
