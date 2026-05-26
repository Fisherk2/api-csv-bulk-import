# Spec: API de Importación/Exportación Masiva con Validación Estricta

## Objective

Build a **REST API with FastAPI** that allows bulk import and export of relational data (orders, products, customers) with **strict Pydantic validation**, **partial processing** (valid rows succeed, invalid rows are reported), **JWT authentication**, and **RFC 7807 error reporting**.

**Purpose:** Portfolio project demonstrating DDD architecture, strict validation, partial batch processing, and production-grade error handling.

**Target users:** Developers evaluating backend architecture skills; no end-user UI.

**Success criteria:**
- `POST /upload` accepts CSV or JSON, validates each row, inserts valid rows, and returns a detailed error report for invalid rows (HTTP 207)
- `GET /export` returns data in CSV or JSON format, filtered by authenticated user
- `POST /token` issues JWT tokens via OAuth2 Password Flow
- All validation errors follow RFC 7807 Problem Details format
- Test coverage ≥ 80%
- `ruff check .` and `mypy .` pass with zero errors
- Docker Compose starts the full stack with one command

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Framework | FastAPI | 0.115+ |
| Validation | Pydantic | 2.x |
| ORM | SQLAlchemy (async) | 2.x |
| Async DB Driver | asyncpg | 0.29+ |
| Sync DB Driver (Alembic) | psycopg2-binary | 2.9+ |
| Async Test DB | aiosqlite | 0.20+ |
| Migrations | Alembic | 1.13+ |
| Database | PostgreSQL | 16 |
| Auth | python-jose + passlib | — |
| Testing | pytest + pytest-cov + pytest-mock + pytest-asyncio | — |
| Linting | ruff | — |
| Type checking | mypy | — |
| Containers | Docker + Docker Compose | — |

---

## Commands

See [AGENTS.md](AGENTS.md) for the full command reference. Quick reference:

```bash
docker-compose up                    # Start PostgreSQL + API
pytest --cov=app                    # Run tests with coverage
ruff check .                        # Lint
mypy .                              # Type check
alembic upgrade head                # Apply migrations
```

---

## Project Structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full directory layout, component diagrams, and technical justifications.

---

## Code Style

See [docs/CODE-STYLE.md](docs/CODE-STYLE.md) for naming conventions, SOLID principles, file rules, pre-commit checks, and prohibited practices.

Key convention summary:

| Category | Convention | Example |
|----------|-----------|---------|
| Pydantic classes | PascalCase + `Schema` suffix | `OrderCreateSchema` |
| SQLAlchemy models | PascalCase + `Model` suffix | `OrderModel` |
| Domain entities | PascalCase (no suffix) | `Order`, `Product` |
| Functions/variables | snake_case | `validate_order`, `order_id` |
| Type hints | Required on all functions | `def create_order(data: OrderCreateSchema) -> Order:` |
| Max file length | 300 lines (except `__init__.py`) | — |

---

## Testing Strategy

See [docs/TESTING.md](docs/TESTING.md) for frameworks, fixtures, examples, quality metrics, and mocking strategy.

| Level | Framework | Location | Coverage Target |
|-------|-----------|----------|----------------|
| **Unit** | pytest + pytest-mock + pytest-asyncio | `tests/unit/` | 90% |
| **Integration** | pytest + httpx.AsyncClient + pytest-asyncio | `tests/integration/` | 80% |
| **E2E** | pytest + httpx.AsyncClient + pytest-asyncio | `tests/e2e/` | 70% |

---

## Boundaries

See [AGENTS.md](AGENTS.md) for the full boundaries list.

- **Always:** Use static typing, include docstrings, validate all inputs, use env vars for secrets, run `pytest` before commits
- **Ask first:** Database schema changes, adding dependencies, changing CI config, modifying `WORKFLOW.md` spec states
- **Never:** Hardcode secrets, use `print` for debugging, ignore exceptions, use raw SQL, skip validation in `ValidationService`, commit failing tests without approval

---

## Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | `POST /upload` accepts CSV and JSON, validates rows, inserts valid data, returns RFC 7807 errors for invalid rows | Integration test: upload mixed valid/invalid data, assert 207 with error details |
| 2 | `GET /export` returns data in CSV or JSON format for authenticated users | E2E test: login → upload → export, verify data integrity |
| 3 | `POST /token` issues JWT tokens via OAuth2 Password Flow | Unit test: valid credentials return token, invalid return 401 |
| 3a | `GET /` returns health check response | Integration test: `GET /` → 200 `{"status": "ok", "version": "1.0.0"}` |
| 3b | CORS middleware allows configured origins | Integration test: preflight request returns correct CORS headers |
| 4 | All validation errors follow RFC 7807 Problem Details format | Unit test: assert error response matches RFC 7807 schema |
| 5 | Test coverage ≥ 80% | `pytest --cov=app --cov-report=term-missing` |
| 6 | `ruff check .` passes with zero errors | `ruff check .` |
| 7 | `mypy .` passes with zero errors | `mypy .` |
| 8 | Docker Compose starts full stack with one command | `docker-compose up` → API responds on port 8000 |
| 9 | Domain layer has zero external dependencies | Verify no DB/HTTP imports in `app/core/` |
| 10 | Partial processing: valid rows succeed even when other rows fail | Integration test: upload 5 valid + 3 invalid rows, assert 5 inserted + 3 errors reported |

---

## Open Questions — RESOLVED

> All open questions have been resolved on 2026-05-25. See [WORKFLOW.md](WORKFLOW.md) for decisions and impact.

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should `/export` support filtering by date range, status, or customer? | **Resolved** | MVP: basic export only — no filters in v1 |
| 2 | What is the maximum batch size for `/upload`? | **Resolved** | 1000 rows — enforced in `BatchUploadRequestSchema` |
| 3 | Should `/upload` support file upload (multipart) or only JSON body? | **Resolved** | JSON body + multipart — both formats supported |
| 4 | Should the API support pagination on `/export`? | **Resolved** | Pagination from v1 — `skip`/`limit` with defaults (0/100) |
| 5 | What is the token expiration time for JWT? | **Resolved** | 30 minutes — configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` |