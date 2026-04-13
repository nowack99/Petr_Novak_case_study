from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.db.repositories.task_repository import TaskRepository
from app.db.repositories.user_repository import UserRepository
from app.dependencies import get_task_repository, get_user_repository
from app.domain.task import TaskStatus
from app.schemas.task import TaskAssign, TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TaskService:
    return TaskService(task_repo, user_repo)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    owner_id: UUID = Query(...),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.create_task(data, owner_id)
    return TaskRead.from_domain(task)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    owner_id: UUID | None = Query(None),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    tasks = await service.list_tasks(owner_id=owner_id, status_filter=status_filter)
    return [TaskRead.from_domain(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.get_task(task_id)
    return TaskRead.from_domain(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    requesting_user_id: UUID = Query(...),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.update_task(task_id, data, requesting_user_id)
    return TaskRead.from_domain(task)


@router.post("/{task_id}/assign", response_model=TaskRead)
async def assign_task(
    task_id: UUID,
    data: TaskAssign,
    requesting_user_id: UUID = Query(...),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.assign_task(task_id, data.assignee_id, requesting_user_id)
    return TaskRead.from_domain(task)


@router.post("/{task_id}/complete", response_model=TaskRead)
async def complete_task(
    task_id: UUID,
    requesting_user_id: UUID = Query(...),
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = await service.complete_task(task_id, requesting_user_id)
    return TaskRead.from_domain(task)
