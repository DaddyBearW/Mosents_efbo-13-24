from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["todo", "in_progress", "done"]


class User(BaseModel):
    id: int
    role: str = Field(pattern="^(user|admin)$")


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str | None = None
    status: TaskStatus
    priority: int = Field(ge=1, le=5)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class Task(TaskCreate):
    id: int
    owner_id: int


class HealthResponse(BaseModel):
    status: str
    env: str


class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]


class AdminStats(BaseModel):
    total_tasks: int
    by_status: dict[TaskStatus, int]
