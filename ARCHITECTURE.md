# Architecture Principles

## Goal

Keep the codebase domain-driven, simple to change, and easy to test.

## Layering

- `app/domain`
  Pure business concepts and rules. No FastAPI, SQLAlchemy, or Pydantic imports.
- `app/services`
  Application use cases. Coordinates repositories and domain objects.
- `app/db/repositories`
  Persistence adapters. Converts ORM models to and from domain objects.
- `app/db/models`
  SQLAlchemy models only.
- `app/api/v1`
  HTTP transport only. Parses requests and formats responses.
- `app/schemas`
  Pydantic models for the API boundary only.

## Dependency Rules

- Dependencies flow inward toward the domain.
- The domain layer must not import from any other project layer.
- Services must not import FastAPI or SQLAlchemy models directly for business rules.
- Routes must not contain business decisions or persistence logic.
- Repositories must not contain business logic.

## Design Guidelines

- Put invariants on domain objects first.
- Prefer immutable domain objects where state transitions matter.
- Keep services thin: orchestration, authorization checks, transaction-friendly coordination.
- Keep repositories boring: query, load, map, save.
- Use explicit types on public functions.
- Prefer small functions with one reason to change.

## Testing Strategy

- Unit-test domain rules without database or HTTP.
- Integration-test routes through the ASGI app.
- Treat services as the main application boundary for behavior.
- Add regression tests for each bug fix.

## Quality Gates

- `ruff` for fast linting and formatting
- `flake8` as an additional style gate
- `mypy` for static typing
- `pytest` for behavior

Run everything with:

```sh
make check
```
