from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.db.repositories.task_repository import TaskRepository
from app.db.repositories.user_repository import UserRepository
from app.domain.ids import TaskId
from app.domain.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        user_repository: UserRepository,
    ) -> None:
        self._tasks = task_repository
        self._users = user_repository

    async def create_task(self, data: TaskCreate, owner_id: UUID) -> Task:
        owner = await self._users.get_by_id(owner_id)
        if owner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{owner_id}' not found.",
            )

        now = datetime.now(tz=UTC)
        task = Task(
            id=TaskId.new(),
            title=data.title,
            description=data.description,
            status=TaskStatus.TODO,
            owner_id=owner.id,
            assignee_id=None,
            created_at=now,
            updated_at=now,
        )

        if data.assignee_id is not None:
            assignee = await self._users.get_by_id(data.assignee_id)
            if assignee is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User '{data.assignee_id}' not found.",
                )
            try:
                task = task.assign_to(assignee)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=str(exc),
                ) from exc

        return await self._tasks.save(task)

    async def get_task(self, task_id: UUID) -> Task:
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task '{task_id}' not found.",
            )
        return task

    async def list_tasks(
        self,
        owner_id: UUID | None = None,
        status_filter: TaskStatus | None = None,
    ) -> list[Task]:
        if owner_id is not None:
            tasks = await self._tasks.get_by_owner(owner_id)
        elif status_filter is not None:
            tasks = await self._tasks.get_by_status(status_filter)
        else:
            tasks = await self._tasks.get_all()

        if owner_id is not None and status_filter is not None:
            tasks = [task for task in tasks if task.status == status_filter]

        return tasks

    async def update_task(
        self,
        task_id: UUID,
        data: TaskUpdate,
        requesting_user_id: UUID,
    ) -> Task:
        task = await self.get_task(task_id)
        requester = await self._users.get_by_id(requesting_user_id)
        if requester is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{requesting_user_id}' not found.",
            )
        if not task.can_be_edited_by(requester):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the active task owner can modify the task.",
            )

        next_status = task.status
        if data.status is not None:
            if task.status == TaskStatus.DONE and data.status != TaskStatus.DONE:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Completed task status cannot be changed.",
                )
            if data.status == TaskStatus.DONE:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Use the complete endpoint to move a task to DONE.",
                )
            next_status = data.status

        updated_task = replace(
            task,
            title=data.title if data.title is not None else task.title,
            description=data.description if data.description is not None else task.description,
            status=next_status,
            updated_at=datetime.now(tz=UTC),
        )
        return await self._tasks.save(updated_task)

    async def assign_task(
        self,
        task_id: UUID,
        assignee_id: UUID,
        requesting_user_id: UUID,
    ) -> Task:
        task = await self.get_task(task_id)
        requester = await self._users.get_by_id(requesting_user_id)
        if requester is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{requesting_user_id}' not found.",
            )
        if not task.can_be_edited_by(requester):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the active task owner can assign the task.",
            )

        assignee = await self._users.get_by_id(assignee_id)
        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{assignee_id}' not found.",
            )

        try:
            updated_task = task.assign_to(assignee)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc

        return await self._tasks.save(updated_task)

    async def complete_task(
        self,
        task_id: UUID,
        requesting_user_id: UUID,
    ) -> Task:
        task = await self.get_task(task_id)
        requester = await self._users.get_by_id(requesting_user_id)
        if requester is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{requesting_user_id}' not found.",
            )
        if not task.can_be_edited_by(requester):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the active task owner can complete the task.",
            )

        try:
            updated_task = task.complete()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc

        return await self._tasks.save(updated_task)
