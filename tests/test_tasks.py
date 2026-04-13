from typing import Any, cast

import pytest
from httpx import AsyncClient
from sqlalchemy import Enum as SqlEnum

from app.db.models.task import TaskModel


async def create_user(
    client: AsyncClient,
    *,
    email: str,
    full_name: str,
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/users",
        json={"email": email, "full_name": full_name, "password": "secret123"},
    )
    assert response.status_code == 201
    return cast(dict[str, Any], response.json())


async def create_task(
    client: AsyncClient,
    *,
    owner_id: str,
    title: str = "Task",
    description: str | None = "Description",
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/tasks",
        params={"owner_id": owner_id},
        json={"title": title, "description": description, "assignee_id": None},
    )
    assert response.status_code == 201
    return cast(dict[str, Any], response.json())


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-create@example.com", full_name="Owner")

    response = await client.post(
        "/api/v1/tasks",
        params={"owner_id": owner["id"]},
        json={"title": "Ship feature", "description": "Implement tasks"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Ship feature"
    assert body["status"] == "todo"
    assert body["owner_id"] == owner["id"]


@pytest.mark.asyncio
async def test_create_task_with_assignee(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-create-assignee@example.com", full_name="Owner")
    assignee = await create_user(
        client,
        email="assignee-create@example.com",
        full_name="Assignee",
    )

    response = await client.post(
        "/api/v1/tasks",
        params={"owner_id": owner["id"]},
        json={
            "title": "Ship feature",
            "description": "Implement tasks",
            "assignee_id": assignee["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["assignee_id"] == assignee["id"]


@pytest.mark.asyncio
async def test_create_task_missing_owner_returns_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tasks",
        params={"owner_id": "00000000-0000-0000-0000-000000000000"},
        json={"title": "Ship feature", "description": "Implement tasks"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_existing(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-get@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.get(f"/api/v1/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


@pytest.mark.asyncio
async def test_get_task_missing(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks_filtered_by_owner(client: AsyncClient) -> None:
    owner_a = await create_user(client, email="owner-a@example.com", full_name="Owner A")
    owner_b = await create_user(client, email="owner-b@example.com", full_name="Owner B")
    await create_task(client, owner_id=owner_a["id"], title="A1")
    await create_task(client, owner_id=owner_a["id"], title="A2")
    await create_task(client, owner_id=owner_b["id"], title="B1")

    response = await client.get("/api/v1/tasks", params={"owner_id": owner_a["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {item["title"] for item in body} == {"A1", "A2"}


@pytest.mark.asyncio
async def test_list_tasks_filtered_by_status(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-status@example.com", full_name="Owner")
    todo_task = await create_task(client, owner_id=owner["id"], title="Todo")
    progress_task = await create_task(client, owner_id=owner["id"], title="Progress")

    await client.patch(
        f"/api/v1/tasks/{progress_task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"status": "in_progress"},
    )

    response = await client.get("/api/v1/tasks", params={"status": "in_progress"})

    assert response.status_code == 200
    body = response.json()
    assert {item["id"] for item in body} == {progress_task["id"]}
    assert all(item["status"] == "in_progress" for item in body)
    assert todo_task["id"] not in {item["id"] for item in body}


@pytest.mark.asyncio
async def test_assign_task(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-assign@example.com", full_name="Owner")
    assignee = await create_user(client, email="assignee@example.com", full_name="Assignee")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/assign",
        params={"requesting_user_id": owner["id"]},
        json={"assignee_id": assignee["id"]},
    )

    assert response.status_code == 200
    assert response.json()["assignee_id"] == assignee["id"]


@pytest.mark.asyncio
async def test_assign_task_missing_assignee_returns_404(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-missing-assignee@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/assign",
        params={"requesting_user_id": owner["id"]},
        json={"assignee_id": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_assign_foreign_task_returns_403(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-foreign-assign@example.com", full_name="Owner")
    stranger = await create_user(client, email="stranger-assign@example.com", full_name="Stranger")
    assignee = await create_user(client, email="assignee-assign2@example.com", full_name="Assignee")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/assign",
        params={"requesting_user_id": stranger["id"]},
        json={"assignee_id": assignee["id"]},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-complete@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    progress_response = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"status": "in_progress"},
    )
    assert progress_response.status_code == 200

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/complete",
        params={"requesting_user_id": owner["id"]},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_complete_task_invalid_transition_returns_422(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-invalid-complete@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.post(
        f"/api/v1/tasks/{task['id']}/complete",
        params={"requesting_user_id": owner["id"]},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_task_success(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-update@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"title": "Updated", "description": "Updated description", "status": "in_progress"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated"
    assert body["description"] == "Updated description"
    assert body["status"] == "in_progress"


@pytest.mark.asyncio
async def test_update_foreign_task_returns_403(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-foreign@example.com", full_name="Owner")
    stranger = await create_user(client, email="stranger@example.com", full_name="Stranger")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": stranger["id"]},
        json={"title": "Hacked"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_task_rejects_blank_title(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-blank@example.com", full_name="Owner")

    response = await client.post(
        "/api/v1/tasks",
        params={"owner_id": owner["id"]},
        json={"title": "   ", "description": "Implement tasks"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_task_done_status_directly_returns_422(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-direct-done@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    response = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"status": "done"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_completed_task_cannot_be_reopened(client: AsyncClient) -> None:
    owner = await create_user(client, email="owner-reopen@example.com", full_name="Owner")
    task = await create_task(client, owner_id=owner["id"])

    await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"status": "in_progress"},
    )
    await client.post(
        f"/api/v1/tasks/{task['id']}/complete",
        params={"requesting_user_id": owner["id"]},
    )

    response = await client.patch(
        f"/api/v1/tasks/{task['id']}",
        params={"requesting_user_id": owner["id"]},
        json={"status": "in_progress"},
    )

    assert response.status_code == 422


def test_task_model_persists_enum_values() -> None:
    status_type = cast(SqlEnum, TaskModel.__table__.c.status.type)
    enum_values = status_type.enums

    assert enum_values == ["todo", "in_progress", "done"]
