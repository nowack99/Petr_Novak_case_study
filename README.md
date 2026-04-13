# Python Developer Live Case Study — Task Management API

A skeleton FastAPI project for evaluating Python developer skills.
The focus is on **clean code**, **proper layer separation**, and **working with domain models**.

---

## Stack

- **FastAPI** + **uvicorn**
- **PostgreSQL 16** (async via `asyncpg`)
- **SQLAlchemy 2** (async ORM)
- **Alembic** migrations
- **Pydantic v2** schemas
- **Docker Compose**

---

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

API docs: http://localhost:8000/docs
Apply migrations (first time):

```bash
docker compose exec api alembic upgrade head
```

---

## Architecture

```
API layer      app/api/v1/         FastAPI routes — HTTP only, no business logic
Service layer  app/services/       Business logic, orchestration
Repository     app/db/repositories/ Data access, ORM ↔ domain mapping
DB models      app/db/models/      SQLAlchemy ORM models (PostgreSQL tables)
Domain models  app/domain/         Pure Python dataclasses — no framework deps
Schemas        app/schemas/        Pydantic v2 — API boundary only
```

**Rule:** dependencies flow downward only. Services never import FastAPI.
Routes never import SQLAlchemy. The domain layer imports nothing from other layers.

---

## What is Pre-built (reference implementations)

| File | Purpose |
|------|---------|
| `app/services/user_service.py` | Complete service — use as reference |
| `app/db/repositories/user_repository.py` | Complete repository + ORM↔domain mapping |
| `app/api/v1/users.py` | Complete route handlers |
| `tests/test_users.py` | Passing tests |

---

## What the Candidate Must Implement

### Tier 1 — Core (required)

| File | What to implement |
|------|-------------------|
| `app/domain/task.py` | `assign_to()`, `complete()`, `can_be_edited_by()` |
| `app/db/repositories/task_repository.py` | `_to_domain()`, `_to_model()`, query methods |
| `app/services/task_service.py` | All service methods |
| `app/api/v1/tasks.py` | All route handlers |

### Tier 2 — Polish

- Implement `tests/test_tasks.py` and `tests/test_domain.py`
- Custom exception classes instead of raising `HTTPException` from the service layer
- Correct HTTP status codes (201, 404, 403, 409)

### Tier 3 — Stretch

- Pagination on `GET /tasks` (limit/offset, return `Page[TaskRead]`)
- `GET /tasks/{task_id}/history` — design a `TaskEvent` model from scratch
- Proper `Depends` chain for service injection (no construction inside handlers)

---

## API Endpoints

### Users
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/users` | Create user |
| `GET` | `/api/v1/users/{user_id}` | Get user by ID |

### Tasks
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/tasks` | Create task |
| `GET` | `/api/v1/tasks` | List tasks (filter by `owner_id`, `task_status`) |
| `GET` | `/api/v1/tasks/{task_id}` | Get task by ID |
| `PATCH` | `/api/v1/tasks/{task_id}` | Update task fields |
| `POST` | `/api/v1/tasks/{task_id}/assign` | Assign task to a user |
| `POST` | `/api/v1/tasks/{task_id}/complete` | Mark task as DONE |

---

## Interview Discussion Points

1. Why three separate model types (DB model / domain model / schema)?
2. What would break if `TaskService` imported from `fastapi` directly?
3. How would you add soft delete to tasks without changing the domain model?
4. What does `expire_on_commit=False` do and why does it matter in async SQLAlchemy?
5. The `Task` dataclass is `frozen=True`. How does that affect `assign_to()` and `complete()`?

---

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run only domain unit tests (no DB needed)
pytest tests/test_domain.py

# With coverage
pytest --cov=app --cov-report=term-missing
```
