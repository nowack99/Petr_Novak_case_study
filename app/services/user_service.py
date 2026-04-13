import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.db.repositories.user_repository import UserRepository
from app.domain.ids import UserId
from app.domain.user import User
from app.schemas.user import UserCreate

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def create_user(self, data: UserCreate) -> User:
        normalized_email = self._normalize_email(data.email)
        existing = await self._repo.get_by_email(normalized_email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{normalized_email}' already exists.",
            )

        hashed_password = _pwd_context.hash(data.password)
        now = datetime.now(tz=UTC)

        user = User(
            id=UserId.new(),
            email=normalized_email,
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

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()
