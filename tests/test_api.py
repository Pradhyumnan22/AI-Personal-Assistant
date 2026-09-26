"""Integration tests for the main API use cases."""

from app.api.dependencies import get_chat_service
from app.main import app


class FakeChatService:
    async def chat(self, content: str, conversation_id: str | None = None):
        return conversation_id or "conversation-1", f"Reply to: {content}", []


def test_chat_endpoint(client):
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService()

    response = client.post("/api/v1/chat", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": "conversation-1",
        "message": "Reply to: Hello",
        "sources": [],
    }


def test_note_crud(client):
    created = client.post(
        "/api/v1/notes", json={"title": "Portfolio", "content": "Build an assistant"}
    )
    assert created.status_code == 201
    note_id = created.json()["id"]

    listed = client.get("/api/v1/notes")
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "Portfolio"

    updated = client.put(
        f"/api/v1/notes/{note_id}",
        json={"title": "Updated", "content": "Ship the assistant"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    deleted = client.delete(f"/api/v1/notes/{note_id}")
    assert deleted.status_code == 204


def test_upload_text_document(client):
    response = client.post(
        "/api/v1/documents",
        files={"file": ("study-plan.txt", b"Review LangGraph every Friday", "text/plain")},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "study-plan"
    assert response.json()["content"] == "Review LangGraph every Friday"


def test_task_crud(client):
    created = client.post(
        "/api/v1/tasks",
        json={"title": "Submit portfolio", "due_at": "2026-10-01T09:00:00Z"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    completed = client.post(f"/api/v1/tasks/{task_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["completed"] is True

    listed = client.get("/api/v1/tasks")
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "Submit portfolio"

    deleted = client.delete(f"/api/v1/tasks/{task_id}")
    assert deleted.status_code == 204


def test_calendar_status(client):
    response = client.get("/api/v1/calendar/status")

    assert response.status_code == 200
    assert response.json()["connected"] is False
