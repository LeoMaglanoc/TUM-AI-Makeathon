.PHONY: up down build test lint format test-unit test-integration

build:
	docker compose build

up:
	docker compose up --build

down:
	docker compose down

test:
	docker compose build backend
	docker compose run --rm backend pytest tests/ -v

test-unit:
	docker compose build backend
	docker compose run --rm backend pytest tests/ -v -k "not integration"

test-integration:
	docker compose build backend
	docker compose run --rm backend pytest tests/ -v -k "integration"

lint:
	docker compose build backend
	docker compose run --rm backend ruff check src/ tests/

format:
	docker compose build backend
	docker compose run --rm backend ruff format src/ tests/
