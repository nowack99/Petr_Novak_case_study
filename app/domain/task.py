from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.ids import TaskId, UserId
from app.domain.user import User


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass(frozen=True)
class Task:
    id: TaskId
    title: str
    status: TaskStatus
    owner_id: UserId
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    assignee_id: UserId | None = None

    def can_be_edited_by(self, user: User) -> bool:
        return user.is_active and user.id == self.owner_id

    def complete(self) -> "Task":
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError("Task can only be completed from IN_PROGRESS status.")

        return replace(
            self,
            status=TaskStatus.DONE,
            updated_at=datetime.now(tz=UTC),
        )

    def assign_to(self, user: User) -> "Task":
        if not user.is_active:
            raise ValueError("Task can only be assigned to an active user.")
        if self.status == TaskStatus.DONE:
            raise ValueError("Completed task cannot be reassigned.")

        return replace(
            self,
            assignee_id=user.id,
            updated_at=datetime.now(tz=UTC),
        )
