# ── API CSV Bulk Import — Makefile ────────────────────────
# Usage: make <target>

.PHONY: help install dev lint format type-check test test-cov run migrate clean docker-build docker-up docker-down docker-logs docker-prod-build docker-prod-up docker-prod-down

# Default values (override with: make dev HOST=127.0.0.1 PORT=9000)
HOST ?= 0.0.0.0
PORT ?= 8000

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production and development dependencies
	pip install -r requirements.txt

dev: ## Start the development server with auto-reload
	uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

run: ## Start the production server (no reload)
	uvicorn app.main:app --host $(HOST) --port $(PORT)

lint: ## Run ruff linter
	ruff check .

format: ## Auto-format code with ruff
	ruff format .

type-check: ## Run mypy type checker (source code only; CI runs full check)
	mypy app/

test: ## Run test suite
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=app --cov-report=term-missing --cov-report=html

migrate: ## Generate and apply Alembic migration (args: message="description")
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head

docker-build: ## Build the Docker image
	docker-compose build

docker-up: ## Start the development stack in background
	docker-compose up -d

docker-down: ## Stop and remove all containers
	docker-compose down

docker-logs: ## Follow Docker logs
	docker-compose logs -f

docker-prod-build: ## Build the production Docker image
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

docker-prod-up: ## Start the production stack in background
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

docker-prod-down: ## Stop the production stack
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

clean: ## Remove Python cache files, build artifacts, and coverage reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ 2>/dev/null || true
	@echo "Cleanup complete."
