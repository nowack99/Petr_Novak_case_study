from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserId:
    value: UUID

    @classmethod
    def new(cls) -> "UserId":
        return cls(uuid4())


@dataclass(frozen=True)
class TaskId:
    value: UUID

    @classmethod
    def new(cls) -> "TaskId":
        return cls(uuid4())
