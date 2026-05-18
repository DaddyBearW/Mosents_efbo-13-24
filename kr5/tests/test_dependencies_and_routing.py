def user_headers(user_id: int, role: str = "user") -> dict[str, str]:
    return {"X-User-Id": str(user_id), "X-User-Role": role}


def create_task(client, user_id: int, role: str = "user", **overrides):
    payload = {
        "title": "Task title",
        "description": "Task description",
        "status": "todo",
        "priority": 3,
    }
    payload.update(overrides)
    return client.post("/tasks", json=payload, headers=user_headers(user_id, role))


def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers=user_headers(10))

    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_missing_x_user_id_returns_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_regular_user_gets_403_on_admin_stats(client):
    response = client.get("/admin/stats", headers=user_headers(10))

    assert response.status_code == 403


def test_admin_gets_stats_for_all_tasks(client):
    create_task(client, 10, title="Todo", status="todo")
    create_task(client, 20, title="Done", status="done")

    response = client.get("/admin/stats", headers=user_headers(1, "admin"))

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 2,
        "by_status": {"todo": 1, "in_progress": 0, "done": 1},
    }


def test_regular_user_cannot_delete_foreign_task(client):
    task_id = create_task(client, 10).json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=user_headers(20))

    assert response.status_code == 404


def test_admin_can_delete_foreign_task(client):
    task_id = create_task(client, 10).json()["id"]

    response = client.delete(f"/admin/tasks/{task_id}", headers=user_headers(1, "admin"))
    after_delete = client.get(f"/tasks/{task_id}", headers=user_headers(10))

    assert response.status_code == 204
    assert after_delete.status_code == 404


def test_openapi_contains_expected_tags(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    tags = {
        operation["tags"][0]
        for path_item in response.json()["paths"].values()
        for operation in path_item.values()
        if "tags" in operation
    }
    assert {"tasks", "users", "admin"}.issubset(tags)
