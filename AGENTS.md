# API de Importación/Exportación Masiva con Validación Estricta

**Versión:** 1.0.0 | **Estado:** En Especificación | **Metodología:** Spec-Driven Development (SDD)
**Repositorio:** https://github.com/Fisherk2/api-csv-bulk-import/

## Quick Reference

- **Stack:** FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Docker, pytest
- **Architecture:** Domain-Driven Design (DDD) with Repository, Service Layer, Unit of Work patterns
- **Auth:** JWT (OAuth2 Password Flow)
- **Error Format:** RFC 7807 (Problem Details)
- **Run:** `docker-compose up` | **Test:** `pytest --cov=app` | **Lint:** `ruff check .` | **Type:** `mypy .`

## Detailed Guidelines

- [Architecture & Design](docs/ARCHITECTURE.md) — Patterns, diagrams, folder structure, technical justifications
- [Domain & Requirements](docs/DOMAIN.md) — Entities, functional/non-functional requirements, system boundaries
- [Code Style & Conventions](docs/CODE-STYLE.md) — Naming, SOLID, file rules, pre-commit checks, prohibited practices
- [Testing Strategy](docs/TESTING.md) — Three-phase strategy, frameworks, fixtures, examples, metrics, mocking
- [Security & Error Handling](docs/SECURITY.md) — Input validation, HTTP responses, rate limiting, secrets, logging

## Implementation Tracking

- [WORKFLOW.md](WORKFLOW.md) — Spec tracking, dependency diagram, phase progress (F0–F6)

## Boundaries

- **Always:** Use static typing (`: type`), include docstrings (Google format), validate all inputs, use env vars for secrets, run `pytest` before commits
- **Ask first:** Database schema changes, adding dependencies, changing CI config, modifying `WORKFLOW.md` spec states
- **Never:** Hardcode secrets, use `print` for debugging, ignore exceptions, use raw SQL, skip validation in `ValidationService`, commit failing tests without approval