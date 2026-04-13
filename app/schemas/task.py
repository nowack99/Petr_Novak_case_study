from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.task import TaskStatus
from app.schemas.user import UserRead


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: UUID | None = None


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


class TaskReadDetailed(TaskRead):
    """TaskRead with nested user objects — use when you need full user info."""
    owner: UserRead
    assignee: UserRead | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: UUID | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
