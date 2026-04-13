from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

if TYPE_CHECKING:
    from app.domain.user import User


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: "User") -> "UserRead":
        return cls(
            id=user.id.value,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
