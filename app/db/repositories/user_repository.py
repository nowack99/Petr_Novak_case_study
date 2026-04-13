from sqlalchemy import select

from app.db.models.user import UserModel
from app.db.repositories.base import BaseRepository
from app.domain.ids import UserId
from app.domain.user import User


class UserRepository(BaseRepository[UserModel, User]):
    model_class = UserModel

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=model.email,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def _to_model(self, domain: User) -> UserModel:
        return UserModel(
            id=domain.id.value,
            email=domain.email,
            full_name=domain.full_name,
            is_active=domain.is_active,
            created_at=domain.created_at,
            # NOTE: hashed_password is not part of the domain model.
            # Use save_with_password() for creation.
            hashed_password="",
        )

    async def save_with_password(self, domain: User, hashed_password: str) -> User:
        model = UserModel(
            id=domain.id.value,
            email=domain.email,
            full_name=domain.full_name,
            is_active=domain.is_active,
            created_at=domain.created_at,
            hashed_password=hashed_password,
        )
        merged = await self._session.merge(model)
        await self._session.flush()
        return self._to_domain(merged)
