.PHONY: up down build restart logs shell migrate makemigration test lint lint-flake8 typecheck check fmt

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

restart:
	docker compose restart api

logs:
	docker compose logs -f api

shell:
	docker compose exec api bash

migrate:
	docker compose exec api alembic upgrade head

makemigration:
	docker compose exec api alembic revision --autogenerate -m "$(name)"

test:
	docker compose exec api pytest

lint:
	docker compose exec api ruff check app tests

lint-flake8:
	docker compose exec api flake8 app tests

typecheck:
	docker compose exec api mypy app tests

check: lint lint-flake8 typecheck test

fmt:
	docker compose exec api ruff format app tests
