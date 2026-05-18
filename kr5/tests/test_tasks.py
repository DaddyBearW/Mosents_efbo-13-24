def headers(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def create_task(client, user_id: int, **overrides):
    payload = {
        "title": "Подготовить тесты",
        "description": "Описание задачи",
        "status": "todo",
        "priority": 4,
    }
    payload.update(overrides)
    return client.post("/tasks", json=payload, headers=headers(user_id))


def test_create_task_success(client):
    response = create_task(client, 10)

    assert response.status_code == 201
    assert response.json()["owner_id"] == 10


def test_create_task_short_title_returns_422(client):
    response = create_task(client, 10, title="no")

    assert response.status_code == 422


def test_missing_user_header_returns_401(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    create_task(client, 10, title="Task 10")
    create_task(client, 20, title="Task 20")

    response = client.get("/tasks", headers=headers(10))

    assert response.status_code == 200
    assert [task["owner_id"] for task in response.json()] == [10]


def test_filter_by_status_and_min_priority(client):
    create_task(client, 10, title="Todo 1", status="todo", priority=1)
    create_task(client, 10, title="Done 5", status="done", priority=5)
    create_task(client, 10, title="Done 3", status="done", priority=3)

    response = client.get(
        "/tasks",
        params={"status": "done", "min_priority": 4},
        headers=headers(10),
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Done 5"]


def test_update_status_success(client):
    task_id = create_task(client, 10).json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers=headers(10),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_foreign_or_missing_task_returns_404(client):
    task_id = create_task(client, 10).json()["id"]

    foreign_response = client.get(f"/tasks/{task_id}", headers=headers(20))
    missing_response = client.get("/tasks/999", headers=headers(10))

    assert foreign_response.status_code == 404
    assert missing_response.status_code == 404


def test_delete_task_success(client):
    task_id = create_task(client, 10).json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers(10))
    after_delete = client.get(f"/tasks/{task_id}", headers=headers(10))

    assert response.status_code == 204
    assert after_delete.status_code == 404


def test_healthcheck(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
