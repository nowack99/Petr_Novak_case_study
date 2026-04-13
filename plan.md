# Task Management Case Study Plan

## Goal

Deliver the missing task-management feature set on top of the existing user management flow, while preserving the project architecture:

- `app/domain`: pure domain objects, no framework imports
- `app/db/repositories`: ORM mapping and persistence only
- `app/services`: business orchestration
- `app/api/v1`: HTTP boundary only
- `app/schemas`: request/response models only

## Current Repository State

Already present:

- `app/db/models/task.py`
- `app/services/task_service.py` as a constructor-only stub
- `app/schemas/task.py` with initial request/response models
- TODO markers in `app/dependencies.py` and `app/api/v1/router.py`

Missing or incomplete:

- `app/domain/task.py`
- `app/db/repositories/task_repository.py`
- `app/api/v1/tasks.py`
- task-specific tests
- full task service implementation

## Implementation Order

### 1. Study the existing user flow

Use these files as the style and layering reference:

- `app/domain/user.py`
- `app/db/repositories/user_repository.py`
- `app/services/user_service.py`
- `app/api/v1/users.py`

Outcome:

- confirm repository patterns
- confirm service error handling style
- match route structure and response serialization

### 2. Implement the task domain

Create `app/domain/task.py` with:

- `TaskStatus` as `StrEnum` with `TODO`, `IN_PROGRESS`, `DONE`
- `Task` as a frozen dataclass

Fields:

- `id: UUID`
- `title: str`
- `status: TaskStatus`
- `owner_id: UUID`
- `created_at: datetime`
- `updated_at: datetime`
- `description: str | None = None`
- `assignee_id: UUID | None = None`

Methods:

- `can_be_edited_by(user: User) -> bool`
- `complete() -> Task`
- `assign_to(user: User) -> Task`

Rules to enforce:

- only owner can edit
- inactive users cannot edit anything
- `complete()` is valid only from `IN_PROGRESS`
- `assign_to()` requires an active assignee
- `DONE` tasks cannot be reassigned
- all mutations return a new instance

### 3. Add repository support

Create `app/db/repositories/task_repository.py` extending `BaseRepository[TaskModel, Task]`.

Implement:

- `_to_domain(model: TaskModel) -> Task`
- `_to_model(domain: Task) -> TaskModel`
- `get_by_owner(owner_id: UUID) -> list[Task]`
- `get_by_assignee(assignee_id: UUID) -> list[Task]`
- `get_by_status(status: TaskStatus) -> list[Task]`

Update `app/dependencies.py`:

- register `get_task_repository`

Notes:

- keep repository free of business rules
- business filtering should stay in service only when it is not a simple query concern

### 4. Finish the service layer

Complete `app/services/task_service.py`.

Required methods:

- `create_task(data: TaskCreate, owner_id: UUID) -> Task`
- `get_task(task_id: UUID) -> Task`
- `list_tasks(owner_id, status) -> list[Task]`
- `update_task(task_id, data: TaskUpdate, requesting_user_id) -> Task`
- `assign_task(task_id, assignee_id, requesting_user_id) -> Task`
- `complete_task(task_id, requesting_user_id) -> Task`

Service responsibilities:

- load task and related user records
- enforce owner-only updates
- call `task.assign_to()` and `task.complete()` instead of mutating fields directly
- map missing resources to `404`
- map permission failures to `403`
- map invalid state transitions to `422`

Implementation detail:

- for `update_task`, build a new immutable `Task` instance with updated fields and refreshed `updated_at`
- if assign-on-create is supported, validate the assignee exists and is active

### 5. Align or extend schemas

Review `app/schemas/task.py` and keep only HTTP-facing concerns there.

Likely final schema set:

- `TaskCreate`
- `TaskUpdate`
- `TaskAssign`
- `TaskRead`

Review whether these should stay or be removed:

- `TaskReadDetailed`
- `TaskStatusUpdate`

Reason:

- the assignment and completion endpoints described in the brief do not require a generic status update API

### 6. Add task routes

Create `app/api/v1/tasks.py`.

Endpoints:

- `POST /api/v1/tasks`
- `GET /api/v1/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/assign`
- `POST /api/v1/tasks/{task_id}/complete`

Then update `app/api/v1/router.py` to register the tasks router.

Route responsibilities:

- parse request bodies and query params
- inject repositories/services via dependencies
- serialize domain objects through Pydantic models
- leave business rules in service/domain

### 7. Add domain unit tests

Create `tests/test_domain.py`.

Cover:

- `Task.can_be_edited_by`
- `Task.complete`
- `Task.assign_to`

Minimum cases:

- owner can edit
- non-owner cannot edit
- inactive user cannot edit
- valid completion transition
- invalid completion transition
- `complete()` returns a new instance
- assign active user
- reject inactive assignee
- reject reassignment when status is `DONE`
- `assign_to()` returns a new instance

### 8. Add HTTP integration tests

Create `tests/test_tasks.py`.

Cover:

- create task
- get existing task
- get missing task
- list tasks filtered by owner
- assign task
- complete task
- attempt to update another user’s task returns `403`

Test setup considerations:

- current test stack uses in-memory SQLite via `Base.metadata.create_all`
- verify the `TaskStatus` enum and UUID columns behave correctly under SQLite
- seed users explicitly in tests before task operations

### 9. Verify end to end

Run:

```sh
make test
```

Manual checks if needed:

- API imports cleanly
- task router is mounted under `/api/v1`
- repository imports do not create circular dependencies

## Suggested Delivery Sequence

Use this order to minimize churn:

1. `app/domain/task.py`
2. `app/db/repositories/task_repository.py`
3. `app/dependencies.py`
4. `app/services/task_service.py`
5. `app/schemas/task.py`
6. `app/api/v1/tasks.py`
7. `app/api/v1/router.py`
8. `tests/test_domain.py`
9. `tests/test_tasks.py`
10. `make test`

## Senior-Level Extensions

Only after the core scope is passing.

### A. Replace HTTPException in services

Introduce domain/service exceptions such as:

- `TaskNotFoundError`
- `PermissionDeniedError`
- `InvalidTransitionError`

Then convert them to HTTP responses at the FastAPI layer through exception handlers.

### B. Add pagination to `GET /api/v1/tasks`

Add:

- `limit: int = 20`
- `offset: int = 0`

Return:

- `items`
- `total`
- `limit`
- `offset`

Use a generic `Page[T]` schema.

### C. Add task history

Implement `GET /api/v1/tasks/{task_id}/history` with:

- history domain object
- ORM model
- migration
- repository
- service method
- automatic recording on each status change

## Definition of Done

The task is complete when:

- domain logic is immutable and validated
- repositories map cleanly between ORM and domain
- services orchestrate task operations without bypassing domain rules
- task routes are registered and working
- unit and integration tests cover the requested cases
- `make test` passes
