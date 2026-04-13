import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.db.repositories.user_repository import UserRepository
from app.domain.user import User
from app.schemas.user import UserCreate

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def create_user(self, data: UserCreate) -> User:
        existing = await self._repo.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{data.email}' already exists.",
            )

        hashed_password = _pwd_context.hash(data.password)
        now = datetime.now(tz=timezone.utc)

        user = User(
            id=uuid.uuid4(),
            email=data.email,
            full_name=data.full_name,
            is_active=True,
            created_at=now,
        )

        return await self._repo.save_with_password(user, hashed_password)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found.",
            )
        return user
