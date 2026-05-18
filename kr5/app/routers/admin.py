from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencies import get_storage, require_admin
from app.schemas import AdminStats, User
from app.storage import TaskStorage


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
def get_stats(
    _: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> AdminStats:
    return AdminStats(**storage.get_stats())


@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(
    task_id: int,
    _: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> Response:
    if storage.delete_task(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
