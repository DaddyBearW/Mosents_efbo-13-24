import importlib.util
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient


MODULE_PATH = Path(__file__).resolve().parents[1] / "main.py"
SPEC = importlib.util.spec_from_file_location("task_11_2_main", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["task_11_2_main"] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


@pytest.fixture(autouse=True)
def clean_state():
    MODULE.reset_state()
    yield
    MODULE.reset_state()


@pytest.fixture
async def client():
    transport = ASGITransport(app=MODULE.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_create_user_returns_201(client, faker) -> None:
    payload = {
        "username": faker.user_name(),
        "age": faker.random_int(min=18, max=60),
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_existing_user_returns_200(client, faker) -> None:
    create_response = await client.post(
        "/users",
        json={
            "username": faker.user_name(),
            "age": faker.random_int(min=18, max=60),
        },
    )

    response = await client.get(f"/users/{create_response.json()['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == create_response.json()["id"]


@pytest.mark.asyncio
async def test_get_missing_user_returns_404(client) -> None:
    response = await client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_existing_user_returns_204(client, faker) -> None:
    create_response = await client.post(
        "/users",
        json={
            "username": faker.user_name(),
            "age": faker.random_int(min=18, max=60),
        },
    )

    response = await client.delete(f"/users/{create_response.json()['id']}")

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_delete_same_user_twice_returns_404(client, faker) -> None:
    create_response = await client.post(
        "/users",
        json={
            "username": faker.user_name(),
            "age": faker.random_int(min=18, max=60),
        },
    )
    user_id = create_response.json()["id"]

    first_delete = await client.delete(f"/users/{user_id}")
    second_delete = await client.delete(f"/users/{user_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 404
    assert second_delete.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_create_user_with_invalid_age_returns_422(client, faker) -> None:
    response = await client.post(
        "/users",
        json={
            "username": faker.user_name(),
            "age": 121,
        },
    )

    assert response.status_code == 422
