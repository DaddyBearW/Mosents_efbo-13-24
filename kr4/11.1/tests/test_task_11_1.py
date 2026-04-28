import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


MODULE_PATH = Path(__file__).resolve().parents[1] / "main.py"
SPEC = importlib.util.spec_from_file_location("task_11_1_main", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["task_11_1_main"] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

client = TestClient(MODULE.app)


@pytest.fixture(autouse=True)
def clean_state():
    MODULE.reset_state()
    yield
    MODULE.reset_state()


def test_create_note_returns_201() -> None:
    response = client.post(
        "/notes",
        json={"title": "Buy milk", "content": "Remember to buy milk"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["done"] is False


def test_get_existing_note_returns_200() -> None:
    created = client.post(
        "/notes",
        json={"title": "Read book", "content": "Read 20 pages"},
    )

    response = client.get(f"/notes/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Read book"


def test_get_missing_note_returns_404() -> None:
    response = client.get("/notes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note_marks_it_done() -> None:
    created = client.post(
        "/notes",
        json={"title": "Workout", "content": "Do 30 push-ups"},
    )

    response = client.patch(f"/notes/{created.json()['id']}", json={"done": True})

    assert response.status_code == 200
    assert response.json()["done"] is True


def test_delete_note_removes_it() -> None:
    created = client.post(
        "/notes",
        json={"title": "Call mom", "content": "In the evening"},
    )

    response = client.delete(f"/notes/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted"
    assert client.get(f"/notes/{created.json()['id']}").status_code == 404


def test_create_note_with_empty_title_returns_422() -> None:
    response = client.post(
        "/notes",
        json={"title": "", "content": "Invalid note"},
    )

    assert response.status_code == 422
