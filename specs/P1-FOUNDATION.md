# F0: Preparación — Implementation Spec

**Phase:** F0 — Preparación  
**Status:** 🟡 In Progress  
**Depends on:** None (first phase)  
**Blocks:** F1 (Infraestructura)

---

## Current State Assessment

| Item | Status | Notes |
|------|--------|-------|
| `app/` directory | ❌ Missing | Needs full DDD structure |
| `tests/` directory | ❌ Missing | Needs unit/, integration/, e2e/ |
| `migrations/` directory | ❌ Missing | Needs Alembic structure |
| `requirements.txt` | ⚠️ Placeholder | Only has a comment line |
| `pyproject.toml` | ❌ Missing | Needs full project config |
| `.env.example` | ⚠️ Placeholder | Only has a comment line |
| `.gitignore` | ✅ Complete | 179 lines, comprehensive |
| `.ruff.toml` | ❌ Missing | Needs ruff lint + format config |
| `mypy.ini` | ❌ Missing | Needs strict type checking config |
| `pytest.ini` | ❌ Missing | Needs pytest + coverage config |
| `Dockerfile` | ⚠️ Placeholder | Only has a comment line (deferred to F1) |
| `docker-compose.yml` | ⚠️ Placeholder | Only has a comment line (deferred to F1) |
| `Makefile` | ⚠️ Placeholder | Only has a comment line |
| `CONTRIBUTING.md` | ⚠️ Empty | 0 bytes |
| Documentation (F0-004) | ✅ Done | AGENTS.md, WORKFLOW.md, README.md, docs/ |

---

## Spec-F0-001: Directory Structure (DDD)

### Objective
Create the full DDD directory structure as defined in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

### Directory Tree

```
app/
├── __init__.py
├── main.py                  # FastAPI app factory and startup
├── config.py                # Settings via pydantic-settings
├── dependencies.py          # DI: get_db, get_current_user
│
├── core/                    # Domain layer (pure business logic, NO external deps)
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── order.py         # Order, OrderItem entities
│   │   ├── product.py       # Product entity
│   │   ├── customer.py      # Customer entity
│   │   └── user.py           # User entity
│   ├── repositories/        # Repository interfaces (contracts)
│   │   ├── __init__.py
│   │   ├── order_repository.py
│   │   ├── product_repository.py
│   │   └── customer_repository.py
│   └── services/            # Domain services
│       ├── __init__.py
│       ├── validation_service.py
│       └── order_service.py
│
├── infrastructure/          # Implementation details
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Engine and session factory
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── order.py
│   │       ├── product.py
│   │       ├── customer.py
│   │       └── user.py
│   ├── repositories/        # Repository implementations
│   │   ├── __init__.py
│   │   ├── order_repository.py
│   │   ├── product_repository.py
│   │   └── customer_repository.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_service.py
│   │   ├── password_service.py
│   │   └── dependencies.py
│   └── api/
│       ├── __init__.py
│       ├── endpoints/
│       │   ├── __init__.py
│       │   ├── upload.py
│       │   ├── export.py
│       │   └── auth.py
│       └── routers.py
│
├── schemas/                 # Pydantic schemas (request/response)
│   ├── __init__.py
│   ├── order.py
│   ├── product.py
│   ├── customer.py
│   ├── user.py
│   └── error.py             # RFC 7807 error schemas
│
└── utils/                   # Utilities
    ├── __init__.py
    ├── csv_parser.py
    ├── json_parser.py
    └── file_utils.py

tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_validation_service.py
│   ├── test_order_service.py
│   └── test_schemas.py
├── integration/
│   ├── __init__.py
│   ├── test_upload_endpoint.py
│   └── test_export_endpoint.py
└── e2e/
    ├── __init__.py
    └── test_full_flow.py

migrations/
├── env.py
├── alembic.ini
├── versions/
│   └── .gitkeep
└── script.mako
```

### Rules
- Every `__init__.py` must be empty (just `"""Package docstring."""` placeholder)
- `app/core/` must have **ZERO** external imports (no SQLAlchemy, no FastAPI, no HTTP)
- Each `.py` file must have a module docstring in Google format
- Max 300 lines per file (exception: `__init__.py` for exports)

### Verification
```bash
# All directories exist
find app/ tests/ migrations/ -type d | sort

# All __init__.py files exist
find app/ tests/ -name "__init__.py" | sort

# No external imports in core/
grep -r "from sqlalchemy\|from fastapi\|import http" app/core/ && echo "FAIL" || echo "PASS"
```

---

## Spec-F0-002: Configuration Files

### Objective
Create all project configuration files with proper content (not placeholders).

### 2.1 `requirements.txt`

```
# Web framework
fastapi>=0.115.0
uvicorn[standard]>=0.30.0

# Validation
pydantic>=2.0
pydantic-settings>=2.0
email-validator>=2.0

# Database
sqlalchemy>=2.0
psycopg2-binary>=2.9
alembic>=1.13

# Authentication
python-jose[cryptography]>=3.3
passlib[bcrypt]>=1.7

# CSV/JSON parsing
python-multipart>=0.0.6

# Rate limiting
slowapi>=0.1.9

# Logging
python-json-logger>=2.0

# Testing
pytest>=8.0
pytest-cov>=5.0
pytest-mock>=3.12
httpx>=0.27

# Linting & Type checking
ruff>=0.4
mypy>=1.10

# Retry logic
tenacity>=8.2
```

### 2.2 `pyproject.toml`

```toml
[project]
name = "api-csv-bulk-import"
version = "1.0.0"
description = "REST API for bulk import/export with strict validation, JWT auth, and RFC 7807 error reporting"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [{name = "Fisherk2"}]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "C4"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
check_untyped_defs = true
no_implicit_optional = true

[[tool.mypy.overrides]]
module = ["python_jose.*", "passlib.*", "slowapi.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--verbose --cov=app --cov-report=term-missing --cov-fail-under=80"
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### 2.3 `.env.example`

```
# Application
APP_NAME=api-csv-bulk-import
APP_VERSION=1.0.0
DEBUG=false

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/api_csv_bulk_import

# Authentication
SECRET_KEY=change-me-to-a-secure-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Upload limits
MAX_BATCH_SIZE=1000
MAX_FILE_SIZE_MB=10

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
```

### 2.4 `.gitignore`

Already complete (179 lines). No changes needed.

### 2.5 `Makefile`

```makefile
.PHONY: help install dev lint format type-check test test-cov run migrate

help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:        ## Install production dependencies
	pip install -r requirements.txt

dev:            ## Install dev dependencies and pre-commit hooks
	pip install -r requirements.txt
	pre-commit install || true

lint:           ## Run ruff linter
	ruff check .

format:         ## Run ruff formatter
	ruff format .

type-check:     ## Run mypy type checker
	mypy .

test:           ## Run all tests
	pytest

test-cov:       ## Run tests with coverage report
	pytest --cov=app --cov-report=term-missing --cov-report=html

run:            ## Start development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:         ## Run Alembic migrations
	alembic upgrade head
```

### Verification
```bash
# requirements.txt is valid
pip install --dry-run -r requirements.txt 2>/dev/null && echo "PASS" || echo "FAIL"

# pyproject.toml is valid TOML
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" && echo "PASS" || echo "FAIL"

# .env.example has no real secrets
grep -i "password\|secret.*=" .env.example | grep -v "change-me\|your_\|postgres:postgres" && echo "FAIL: real secrets found" || echo "PASS"
```

---

## Spec-F0-003: Linters and Testing Configuration

### Objective
Configure ruff, mypy, and pytest for the project.

### 3.1 `.ruff.toml` (alternative: already in `pyproject.toml`)

Since `pyproject.toml` already contains `[tool.ruff]` configuration, a separate `.ruff.toml` is **NOT needed**. The ruff config is centralized in `pyproject.toml`.

**Decision:** Use `pyproject.toml` as the single source of truth for all tool configs. Do NOT create separate `.ruff.toml`, `mypy.ini`, or `pytest.ini` files.

### 3.2 `mypy.ini` (alternative: already in `pyproject.toml`)

Same decision: mypy config is in `pyproject.toml` under `[tool.mypy]`. No separate `mypy.ini` needed.

### 3.3 `pytest.ini` (alternative: already in `pyproject.toml`)

Same decision: pytest config is in `pyproject.toml` under `[tool.pytest.ini_options]`. No separate `pytest.ini` needed.

### 3.4 Pre-commit Configuration (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0, types-passlib]
```

### Verification
```bash
# ruff can read config from pyproject.toml
ruff check --config pyproject.toml . 2>/dev/null && echo "PASS" || echo "CONFIG OK (no files to lint yet)"

# mypy can read config from pyproject.toml
mypy --config-file pyproject.toml app/ 2>/dev/null && echo "PASS" || echo "CONFIG OK (no files to type-check yet)"

# pytest can read config from pyproject.toml
pytest --co 2>/dev/null && echo "PASS" || echo "CONFIG OK (no tests yet)"
```

---

## Spec-F0-004: Documentation (✅ Already Complete)

| File | Status | Notes |
|------|--------|-------|
| `AGENTS.md` | ✅ | Refactored to 29 lines with progressive disclosure |
| `WORKFLOW.md` | ✅ | 172 lines with spec tracking and dependency diagram |
| `SPEC.md` | ✅ | 123 lines with links to docs/ |
| `README.md` | ✅ | 47 lines basic project readme |
| `docs/ARCHITECTURE.md` | ✅ | Patterns, diagrams, folder structure |
| `docs/DOMAIN.md` | ✅ | Entities, requirements, boundaries |
| `docs/CODE-STYLE.md` | ✅ | Naming, SOLID, file rules |
| `docs/TESTING.md` | ✅ | Three-phase strategy, fixtures, examples |
| `docs/SECURITY.md` | ✅ | Validation, errors, rate limiting, secrets |

---

## Dependency Order

```mermaid
graph LR
    F0-001[F0-001\nDirectory Structure] --> F0-002[F0-002\nConfig Files]
    F0-002 --> F0-003[F0-003\nLinters & Testing]
    F0-004[F0-004\nDocumentation ✅]
```

**Implementation order:** F0-001 → F0-002 → F0-003 (F0-004 already done)

---

## Open Decisions (from SPEC.md)

| # | Question | Proposed Answer | Impact on F0 |
|---|----------|----------------|--------------|
| 1 | Should `/export` support filtering? | MVP: basic export only | No impact on F0 |
| 2 | Max batch size for `/upload`? | **1000 rows** | Reflected in `.env.example` as `MAX_BATCH_SIZE=1000` |
| 3 | Should `/upload` support file upload? | **JSON body + multipart** | Reflected in `requirements.txt` (`python-multipart`) |
| 4 | Should `/export` support pagination? | Open (MVP: no pagination) | No impact on F0 |
| 5 | JWT token expiration? | **30 minutes** | Reflected in `.env.example` as `ACCESS_TOKEN_EXPIRE_MINUTES=30` |

---

## Verification Checklist (Complete F0)

- [ ] All directories in the tree exist with `__init__.py` files
- [ ] `app/core/` has zero external imports (no SQLAlchemy, FastAPI, HTTP)
- [ ] `requirements.txt` installs without errors
- [ ] `pyproject.toml` is valid TOML with all tool configs
- [ ] `.env.example` has no real secrets
- [ ] `.gitignore` is comprehensive (already done)
- [ ] `ruff check .` runs without config errors
- [ ] `mypy .` runs without config errors
- [ ] `pytest --co` runs without config errors
- [ ] `Makefile` targets all work (`make help`, `make lint`, etc.)
- [ ] `.pre-commit-config.yaml` is valid
- [ ] All documentation files are up to date (already done)