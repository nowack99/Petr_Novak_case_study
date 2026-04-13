from uuid import UUID

from app.db.repositories.task_repository import TaskRepository
from app.db.repositories.user_repository import UserRepository
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


