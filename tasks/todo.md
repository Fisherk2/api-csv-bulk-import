# TODO: API de Importación/Exportación Masiva con Validación Estricta

**Methodology:** Vertical Slice Planning (SDD)
**Last Updated:** 2026-05-28
**Full Plan:** [tasks/plan.md](plan.md)

---

## Phase 1: Foundation ✅ Completed (2026-05-25)

- [x] **T01** — Directory Structure (DDD) — `app/`, `tests/`, `migrations/` with all `__init__.py` files
- [x] **T02** — Configuration Files — `requirements.txt`, `pyproject.toml`, `.env.example`, `Makefile`
- [x] **T03** — Linters & Pre-commit — `.pre-commit-config.yaml`, verify ruff/mypy/pytest configs

### ✅ Checkpoint: Foundation — PASSED
- [x] All directories exist with `__init__.py`
- [x] `pip install -r requirements.txt` succeeds (format correct; PEP 668 on system env is not a requirements issue)
- [x] `ruff check .`, `mypy .`, `pytest --co` run without config errors
- [x] `make help` prints all targets
- [x] `app/core/` has zero external imports (verified by AST tests)
- [x] Code review passed — 5 axes: Correctness, Readability, Architecture, Security, Performance

**Summary:** 33 tests passing, ruff zero issues, mypy zero issues. 8 commits on `feature/api-import-export`.

---

## Phase 2: Auth Vertical Slice ✅ Completed (2026-05-28)

> **Spec:** [specs/P2-AUTH-SLICE.md](../specs/P2-AUTH-SLICE.md)
> **Architectural Decisions:** Async SQLAlchemy (AD-P2-01), Test fixtures (AD-P2-02), Health check (AD-P2-03), CORS (AD-P2-04)

- [x] **T04** — Database Setup + Alembic (async) — `config.py`, `base.py` (DeclarativeBase), `session.py` (async), Alembic init, `requirements.txt` update, `.env.example` update
- [x] **T05** — SQLAlchemy Base + User Model — `UserModel` with `Mapped` type annotations, migration for `users` table
- [x] **T06** — User Entity + Auth Schemas — `User` entity (dataclass), `TokenSchema`, `UserCreateSchema`, `ProblemDetailSchema` (RFC 7807)
- [x] **T07** — JWT Auth + /token + GET / + CORS — `jwt_service.py`, `password_service.py`, `dependencies.py` (async), `/token`, `GET /`, `main.py` with CORS

### ✅ Checkpoint: Auth Vertical Slice — PASSED
- [x] `POST /token` returns JWT for valid credentials, 401 for invalid
- [x] `get_current_user` dependency validates JWT tokens
- [x] `GET /` returns `{"status": "ok", "version": "1.0.0"}`
- [x] Swagger UI at `/docs` shows `/token` and `GET /` endpoints
- [x] CORS middleware configured with configurable origins
- [x] `ruff check .` and `mypy .` pass
- [x] All P2 unit and integration tests pass (77 tests)
- [x] `app/core/` has zero external imports
- [x] Code review passed — 5 axes: Correctness, Readability, Architecture, Security, Performance

**Summary:** 77 tests passing, coverage 80.88%, ruff zero issues, mypy zero issues. 7 commits on `feature/api-import-export` (d51f990 → 508f4a5). P3 (Product Slice) ready for specs.

**Technical decisions:** SQLAlchemy async with `asyncpg` + `psycopg2` for Alembic; direct bcrypt (passlib incompatible with bcrypt 5.0); test fixtures with SQLite in-memory; `func.now()` replaced by `datetime.now(timezone.utc)` for SQLite compatibility.

---

## Phase 3: Product Vertical Slice

- [ ] **T08** — Product Entity + Schemas — `Product` entity, `ProductCreateSchema`, `ProductResponseSchema`
- [ ] **T09** — Product Model + Repository — `ProductModel`, `IProductRepository`, `ProductRepository`, migration

---

## Phase 4: Customer + Order Upload Slice

- [ ] **T10** — Customer Entity + Schemas — `Customer` entity, `CustomerCreateSchema`, `CustomerResponseSchema`
- [ ] **T11** — Customer Model + Repository — `CustomerModel`, `ICustomerRepository`, `CustomerRepository`, migration
- [ ] **T12** — Order + OrderItem Entities + Schemas — `Order`, `OrderItem` entities, `BatchUploadRequestSchema`, `BatchUploadResponseSchema`
- [ ] **T13** — Order Model + Repository — `OrderModel`, `OrderItemModel`, `IOrderRepository`, `OrderRepository`, migration
- [ ] **T14** — Validation Service — `ValidationService.validate_batch()` with RFC 7807 error format
- [ ] **T15** — Order Service — `OrderService.upload_orders()` orchestrating validation + persistence
- [ ] **T16** — CSV/JSON Parsers — `csv_parser.py`, `json_parser.py`, `file_utils.py`
- [ ] **T17** — /upload Endpoint — `POST /upload` with auth, validation, partial processing (200/207/422)

### ✅ Checkpoint: Upload Vertical Slice
- [ ] Authenticated `POST /upload` with valid JSON → 200
- [ ] Authenticated `POST /upload` with mixed valid/invalid → 207 with RFC 7807 errors
- [ ] Authenticated `POST /upload` with all invalid → 422
- [ ] Unauthenticated request → 401
- [ ] `ruff check .` and `mypy .` pass

---

## Phase 5: Export Vertical Slice

- [ ] **T18** — /export Endpoint — `GET /export` with JSON/CSV format negotiation, pagination (`skip`/`limit`), auth required

### ✅ Checkpoint: Full Upload → Export Flow
- [ ] Full E2E flow: `POST /token` → `POST /upload` → `GET /export` works
- [ ] Data integrity: uploaded data matches exported data
- [ ] `ruff check .` and `mypy .` pass

---

## Phase 6: Testing

- [ ] **T19** — Unit Tests — Validation Service + Schemas (`tests/unit/test_validation_service.py`, `test_schemas.py`)
- [ ] **T20** — Unit Tests — Order Service + Repositories (`tests/unit/test_order_service.py`, `test_repositories.py`)
- [ ] **T21** — Integration Tests — /upload Endpoint (`tests/integration/test_upload_endpoint.py`)
- [ ] **T22** — Integration Tests — /export Endpoint (`tests/integration/test_export_endpoint.py`)
- [ ] **T23** — E2E Tests — Full Flow (`tests/e2e/test_full_flow.py`)

### ✅ Checkpoint: Testing Complete
- [ ] `pytest` — all tests pass
- [ ] `pytest --cov=app` — coverage ≥ 80%
- [ ] `ruff check .` — zero errors
- [ ] `mypy .` — zero type errors

---

## Phase 7: Deployment

- [ ] **T24** — Docker Dev Setup — Multi-stage `Dockerfile`, `docker-compose.yml` (PostgreSQL + API)
- [ ] **T25** — Docker Prod + CI/CD — `docker-compose.prod.yml`, `.github/workflows/ci.yml`

---

## Phase 8: Closure

- [ ] **T26** — Final Documentation — Update `README.md`, `AGENTS.md`, `WORKFLOW.md` with completed state
- [ ] **T27** — User Guide — `USER_GUIDE.md` with `curl` examples for all endpoints
- [ ] **T28** — Retrospective — Lessons learned, `CONTRIBUTING.md`, resolve SPEC.md open questions

---

## Progress Summary

| Phase | Tasks | Completed | Status |
|-------|-------|-----------|--------|
| 1. Foundation | 3 | 3 | ✅ Completed |
| 2. Auth Slice | 4 | 4 | ✅ Completed |
| 3. Product Slice | 2 | 0 | ❌ Not started |
| 4. Upload Slice | 8 | 0 | ❌ Not started |
| 5. Export Slice | 1 | 0 | ❌ Not started |
| 6. Testing | 5 | 0 | ❌ Not started |
| 7. Deployment | 2 | 0 | ❌ Not started |
| 8. Closure | 3 | 0 | ❌ Not started |
| **Total** | **28** | **7** | 🟡 In Progress |