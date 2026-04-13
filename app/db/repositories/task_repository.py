from uuid import UUID

from sqlalchemy import select

from app.db.models.task import TaskModel
from app.db.repositories.base import BaseRepository
from app.domain.ids import TaskId, UserId
from app.domain.task import Task, TaskStatus


class TaskRepository(BaseRepository[TaskModel, Task]):
    model_class = TaskModel

    async def get_all(self) -> list[Task]:
        result = await self._session.execute(select(TaskModel))
        return [self._to_domain(model) for model in result.scalars().all()]

    async def get_by_owner(self, owner_id: UUID) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.owner_id == owner_id)
        )
        return [self._to_domain(model) for model in result.scalars().all()]

    async def get_by_assignee(self, assignee_id: UUID) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.assignee_id == assignee_id)
        )
        return [self._to_domain(model) for model in result.scalars().all()]

    async def get_by_status(self, status: TaskStatus) -> list[Task]:
        result = await self._session.execute(
            select(TaskModel).where(TaskModel.status == status)
        )
        return [self._to_domain(model) for model in result.scalars().all()]

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=TaskId(model.id),
            title=model.title,
            description=model.description,
            status=model.status,
            owner_id=UserId(model.owner_id),
            assignee_id=UserId(model.assignee_id) if model.assignee_id is not None else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, domain: Task) -> TaskModel:
        return TaskModel(
            id=domain.id.value,
            title=domain.title,
            description=domain.description,
            status=domain.status,
            owner_id=domain.owner_id.value,
            assignee_id=domain.assignee_id.value if domain.assignee_id is not None else None,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )
