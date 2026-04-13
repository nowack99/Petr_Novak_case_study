import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={"email": "alice@example.com", "full_name": "Alice", "password": "secret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice"
    assert body["is_active"] is True
    assert "id" in body


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "bob@example.com", "full_name": "Bob", "password": "secret123"}
    await client.post("/api/v1/users", json=payload)
    response = await client.post("/api/v1/users", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/v1/users",
        json={"email": "charlie@example.com", "full_name": "Charlie", "password": "pass"},
    )
    user_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
