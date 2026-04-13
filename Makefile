.PHONY: up down build restart logs shell migrate makemigration test lint fmt

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
	ruff check app tests

fmt:
	ruff format app tests
