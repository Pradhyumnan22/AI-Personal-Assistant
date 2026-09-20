"""Task and reminder endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import DatabaseSession
from app.core.security import verify_api_key
from app.db.repositories import TaskRepository
from app.schemas.tasks import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/api/v1/tasks", dependencies=[Depends(verify_api_key)]
)


@router.get("", response_model=list[TaskResponse])
def list_tasks(session: DatabaseSession, include_completed: bool = True):
    return TaskRepository(session).list(include_completed)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, session: DatabaseSession):
    return TaskRepository(session).create(payload.title, payload.due_at)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, session: DatabaseSession):
    repository = TaskRepository(session)
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return repository.update(task, payload.title, payload.due_at, payload.completed)


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, session: DatabaseSession):
    repository = TaskRepository(session)
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return repository.complete(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, session: DatabaseSession) -> Response:
    repository = TaskRepository(session)
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    repository.delete(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
