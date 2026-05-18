from collections import Counter
from typing import Any

from fastapi import WebSocket

from app.schemas import Task, TaskCreate


class TaskStorage:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.tasks: dict[int, Task] = {}
        self.next_id = 1

    def create_task(self, payload: TaskCreate, owner_id: int) -> Task:
        task = Task(id=self.next_id, owner_id=owner_id, **payload.model_dump())
        self.tasks[task.id] = task
        self.next_id += 1
        return task

    def list_tasks(
        self,
        owner_id: int,
        status: str | None = None,
        min_priority: int | None = None,
    ) -> list[Task]:
        result = [task for task in self.tasks.values() if task.owner_id == owner_id]
        if status is not None:
            result = [task for task in result if task.status == status]
        if min_priority is not None:
            result = [task for task in result if task.priority >= min_priority]
        return sorted(result, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id)

    def update_status(self, task_id: int, status: str) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None:
            return None
        updated = task.model_copy(update={"status": status})
        self.tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: int) -> Task | None:
        return self.tasks.pop(task_id, None)

    def get_stats(self) -> dict[str, Any]:
        counts = Counter(task.status for task in self.tasks.values())
        by_status = {
            "todo": counts.get("todo", 0),
            "in_progress": counts.get("in_progress", 0),
            "done": counts.get("done", 0),
        }
        return {"total_tasks": len(self.tasks), "by_status": by_status}


class RoomManager:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.rooms: dict[str, list[dict[str, Any]]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms.setdefault(room_id, []).append(
            {"username": username, "websocket": websocket}
        )

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        room = self.rooms.get(room_id, [])
        self.rooms[room_id] = [
            item
            for item in room
            if not (item["username"] == username and item["websocket"] is websocket)
        ]
        if not self.rooms[room_id]:
            self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict[str, Any]) -> None:
        for item in list(self.rooms.get(room_id, [])):
            await item["websocket"].send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return [item["username"] for item in self.rooms.get(room_id, [])]


task_storage = TaskStorage()
room_manager = RoomManager()
