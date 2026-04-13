from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.ids import TaskId, UserId
from app.domain.task import Task, TaskStatus
from app.domain.user import User


def make_user(*, is_active: bool = True) -> User:
    return User(
        id=UserId(uuid4()),
        email="user@example.com",
        full_name="User",
        is_active=is_active,
        created_at=datetime.now(tz=UTC),
    )


def make_task(*, owner_id: UserId | None = None, status: TaskStatus = TaskStatus.TODO) -> Task:
    now = datetime.now(tz=UTC)
    return Task(
        id=TaskId(uuid4()),
        title="Test task",
        description="Description",
        status=status,
        owner_id=owner_id if owner_id is not None else UserId(uuid4()),
        assignee_id=None,
        created_at=now,
        updated_at=now,
    )


def test_task_can_be_edited_by_owner() -> None:
    user = make_user()
    task = make_task(owner_id=user.id)

    assert task.can_be_edited_by(user) is True


def test_task_cannot_be_edited_by_non_owner() -> None:
    task = make_task()
    user = make_user()

    assert task.can_be_edited_by(user) is False


def test_task_cannot_be_edited_by_inactive_user() -> None:
    user = make_user(is_active=False)
    task = make_task(owner_id=user.id)

    assert task.can_be_edited_by(user) is False


def test_task_complete_allows_valid_transition() -> None:
    task = make_task(status=TaskStatus.IN_PROGRESS)

    completed = task.complete()

    assert completed.status == TaskStatus.DONE


def test_task_complete_rejects_invalid_transition() -> None:
    task = make_task(status=TaskStatus.TODO)

    with pytest.raises(ValueError, match="IN_PROGRESS"):
        task.complete()


def test_task_complete_returns_new_instance() -> None:
    task = make_task(status=TaskStatus.IN_PROGRESS)

    completed = task.complete()

    assert completed is not task
    assert completed.updated_at >= task.updated_at


def test_task_assign_to_active_user() -> None:
    task = make_task()
    user = make_user()

    assigned = task.assign_to(user)

    assert assigned.assignee_id == user.id


def test_task_assign_to_rejects_inactive_user() -> None:
    task = make_task()
    user = make_user(is_active=False)

    with pytest.raises(ValueError, match="active user"):
        task.assign_to(user)


def test_task_assign_to_rejects_done_task() -> None:
    task = make_task(status=TaskStatus.DONE)
    user = make_user()

    with pytest.raises(ValueError, match="Completed task"):
        task.assign_to(user)


def test_task_assign_to_returns_new_instance() -> None:
    task = make_task()
    user = make_user()

    assigned = task.assign_to(user)

    assert assigned is not task
    assert assigned.updated_at >= task.updated_at
    assert task.assignee_id is None
