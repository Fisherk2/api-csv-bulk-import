# TODO: API de Importación/Exportación Masiva con Validación Estricta

**Methodology:** Vertical Slice Planning (SDD)
**Last Updated:** 2026-05-25
**Full Plan:** [tasks/plan.md](plan.md)

---

## Phase 1: Foundation

- [ ] **T01** — Directory Structure (DDD) — `app/`, `tests/`, `migrations/` with all `__init__.py` files
- [ ] **T02** — Configuration Files — `requirements.txt`, `pyproject.toml`, `.env.example`, `Makefile`
- [ ] **T03** — Linters & Pre-commit — `.pre-commit-config.yaml`, verify ruff/mypy/pytest configs

### ✅ Checkpoint: Foundation
- [ ] All directories exist with `__init__.py`
- [ ] `pip install -r requirements.txt` succeeds
- [ ] `ruff check .`, `mypy .`, `pytest --co` run without config errors
- [ ] `make help` prints all targets
- [ ] `app/core/` has zero external imports

---

## Phase 2: Auth Vertical Slice

- [ ] **T04** — Database Setup + Alembic — `config.py`, `base.py`, `session.py`, Alembic init
- [ ] **T05** — SQLAlchemy Base + User Model — `UserModel`, migration for `users` table
- [ ] **T06** — User Entity + Auth Schemas — `User` entity, `TokenSchema`, `UserCreateSchema`, `ProblemDetailSchema`
- [ ] **T07** — JWT Auth + /token Endpoint — `jwt_service.py`, `password_service.py`, `dependencies.py`, `/token`, `main.py`

### ✅ Checkpoint: Auth Vertical Slice
- [ ] `POST /token` returns JWT for valid credentials, 401 for invalid
- [ ] `get_current_user` dependency validates JWT tokens
- [ ] Swagger UI at `/docs` shows `/token` endpoint
- [ ] `ruff check .` and `mypy .` pass

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
| 1. Foundation | 3 | 0 | ❌ Not started |
| 2. Auth Slice | 4 | 0 | ❌ Not started |
| 3. Product Slice | 2 | 0 | ❌ Not started |
| 4. Upload Slice | 8 | 0 | ❌ Not started |
| 5. Export Slice | 1 | 0 | ❌ Not started |
| 6. Testing | 5 | 0 | ❌ Not started |
| 7. Deployment | 2 | 0 | ❌ Not started |
| 8. Closure | 3 | 0 | ❌ Not started |
| **Total** | **28** | **0** | ❌ Not started |