from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: add startup logic here if needed (e.g. warm-up connections)
    yield
    # TODO: add shutdown logic here if needed


app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="Live case study skeleton — Task Management API",
    lifespan=lifespan,
)

app.include_router(v1_router, prefix="/api/v1")
