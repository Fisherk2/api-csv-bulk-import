# ── API CSV Bulk Import — Makefile ────────────────────────
# Usage: make <target>

.PHONY: help install dev lint format type-check test test-cov run migrate clean

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

type-check: ## Run mypy type checker
	mypy .

test: ## Run test suite
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=app --cov-report=term-missing --cov-report=html

migrate: ## Generate and apply Alembic migration (args: message="description")
	alembic revision --autogenerate -m "$(message)"
	alembic upgrade head

clean: ## Remove Python cache files, build artifacts, and coverage reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ 2>/dev/null || true
	@echo "Cleanup complete."
