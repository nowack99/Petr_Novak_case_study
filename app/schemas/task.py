from datetime import datetime
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.domain.task import TaskStatus

if TYPE_CHECKING:
    from app.domain.task import Task

TaskTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class TaskCreate(BaseModel):
    title: TaskTitle
    description: str | None = None
    assignee_id: UUID | None = None


class TaskAssign(BaseModel):
    assignee_id: UUID


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    owner_id: UUID
    assignee_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task: "Task") -> "TaskRead":
        return cls(
            id=task.id.value,
            title=task.title,
            description=task.description,
            status=task.status,
            owner_id=task.owner_id.value,
            assignee_id=task.assignee_id.value if task.assignee_id is not None else None,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskUpdate(BaseModel):
    title: TaskTitle | None = None
    description: str | None = None
    status: TaskStatus | None = None
