from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.db.repositories.user_repository import UserRepository
from app.dependencies import get_user_repository
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = await service.create_user(data)
    return UserRead.from_domain(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = await service.get_user(user_id)
    return UserRead.from_domain(user)
