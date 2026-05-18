from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.dependencies import get_current_user, get_storage
from app.schemas import Task, TaskCreate, TaskStatusUpdate, User
from app.storage import TaskStorage


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create_task(
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    return storage.create_task(payload, owner_id=user.id)


@router.get("", response_model=list[Task])
def list_tasks(
    status: str | None = Query(default=None),
    min_priority: int | None = Query(default=None, ge=1, le=5),
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> list[Task]:
    return storage.list_tasks(user.id, status=status, min_priority=min_priority)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    task = storage.get_task(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    task = storage.get_task(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.update_status(task_id, payload.status)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Response:
    task = storage.get_task(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.delete_task(task_id)
    return Response(status_code=204)
