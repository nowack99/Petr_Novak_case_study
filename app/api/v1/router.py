from fastapi import APIRouter

from app.api.v1 import tasks, users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
