from abc import abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class BaseRepository[ModelT: Base, DomainT]:
    model_class: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: UUID) -> DomainT | None:
        result = await self._session.execute(
            select(self.model_class).where(self.model_class.id == id)  # type: ignore[attr-defined]
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    async def save(self, domain_obj: DomainT) -> DomainT:
        model = self._to_model(domain_obj)
        merged = await self._session.merge(model)
        await self._session.flush()
        return self._to_domain(merged)

    async def delete(self, id: UUID) -> bool:
        result = await self._session.execute(
            select(self.model_class).where(self.model_class.id == id)  # type: ignore[attr-defined]
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    @abstractmethod
    def _to_domain(self, model: ModelT) -> DomainT:
        raise NotImplementedError

    @abstractmethod
    def _to_model(self, domain: DomainT) -> ModelT:
        raise NotImplementedError
