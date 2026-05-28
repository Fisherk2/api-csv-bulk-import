# Retrospective — v1.0.0

**Date:** 2026-06-06
**Project:** Bulk Import/Export API with Strict Validation
**Author:** Fisherk2

---

## Summary

Built a production-grade REST API for bulk import/export of relational data using FastAPI, SQLAlchemy async, PostgreSQL, and DDD architecture. Delivered across 8 vertical-slice phases (P1–P8) over 12 days, from empty directory to deployed Docker stack with CI/CD.

**Final metrics:** 279 tests, 97.24% coverage, 0 ruff issues, 0 mypy errors, 53 source files (2,622 LOC), 40 test files (5,072 LOC).

---

## What Went Well

### Vertical Slices Delivered

The shift from horizontal phases (F0–F6) to vertical slices (P1–P8) was the right call. Each phase delivered complete, testable functionality end-to-end. By P4 (Upload), we had a working API from database to endpoint. This momentum kept motivation high and reduced integration risk.

### DDD Architecture Held

The dependency rule — domain layer with zero external imports — was enforced from day one and never violated. Repository interfaces (ABC) made swapping implementations trivial during testing. The architecture stayed clean even under pressure to "just make it work."

### Test Coverage as a Safety Net

Starting tests alongside code (not after) meant regressions were caught immediately. The three-phase strategy (unit → integration → E2E) scaled well. Docker smoke tests validated the production stack without slowing the fast feedback loop.

### Partial Processing Design

The 200/207/422 response pattern for batch uploads was elegant. Valid rows succeed even when others fail — this is exactly what users need for bulk operations. RFC 7807 error format made debugging straightforward.

### Rate Limiting Integration

slowapi was painless to integrate. The module-level singleton pattern kept the limiter state clean. Moving rate limiting to P7 (instead of P4) was correct — it's an infrastructure concern, not a business feature.

---

## What Could Improve

### Schema Evolution During Development

Early schema decisions (e.g., `customer_id` as required UUID) constrained later iterations. Customer resolution (find by email or create during upload) was deferred because the schema assumed customers existed beforehand. **Lesson:** Design schemas with "happy path + escape hatch" from the start.

### Test Organization

Tests were built alongside features (correct) but the organization evolved organically. Some test files grew large before being split. **Lesson:** Establish test file size limits (e.g., 200 lines) and split proactively.

### Documentation Timing

Documentation was deferred to P8 (correct per SDD) but meant the README was stale for most of the project. **Lesson:** Keep a minimal README updated after each phase. The "portfolio-quality" rewrite can still be deferred.

### Migration Conflicts

Alembic migration conflicts required manual resolution twice. **Lesson:** Name migrations descriptively and review before committing. Consider `alembic merge` earlier when parallel branches exist.

### Error Message Specificity

Some validation errors were too generic ("Field required"). Row-specific context (which field, which row) improved over time but could be better. **Lesson:** Include row_number and field name in every validation error from the start.

---

## Technical Decisions Worth Repeating

| Decision | Why It Worked |
|----------|---------------|
| SQLAlchemy async with asyncpg | Clean async/await throughout the stack |
| ABC repository interfaces | Swappable implementations, testable domain |
| Pydantic v2 with `model_validate` | Strict validation, clear error messages |
| `ON CONFLICT DO NOTHING` for batch insert | True partial processing without complex logic |
| slowapi for rate limiting | Minimal integration, configurable per-endpoint |
| Multi-stage Docker build | Small production images (<300 MB) |
| Nginx reverse proxy | Security headers, request size limits, SSL termination |

## Technical Decisions to Reconsider

| Decision | What to Change |
|----------|---------------|
| `customer_id` required in upload | Support email-based customer resolution |
| No CHANGELOG.md | Add one for multi-version projects |
| `created_at`/`updated_at` in Core insert | Use ORM defaults where possible |

---

## Future Enhancements

### Priority: High

- **Customer resolution during upload** — find by email or create automatically (currently requires pre-seeded customers)
- **Filtering on `/export`** — date range, status, customer filters
- **Webhook notifications** — notify external systems on upload completion

### Priority: Medium

- **Streaming export** — handle millions of rows without memory issues
- **CSV template download** — generate a template CSV with correct headers
- **Batch progress tracking** — WebSocket or SSE for large uploads
- **OpenTelemetry integration** — distributed tracing across services

### Priority: Low

- **GraphQL endpoint** — for flexible querying
- **API versioning** — `/v1/` prefix for backward compatibility
- **Multi-tenant support** — tenant isolation via middleware
- **Rate limit dashboard** — visualize usage patterns

---

## Process Lessons

### Spec-Driven Development Works

Writing specs before code prevented scope creep and kept the project focused. The `specs/` directory became the source of truth. Every task traced back to a spec. This discipline is worth the upfront investment.

### Vertical > Horizontal

The original F0–F6 plan was logical but would have delivered working code much later. Vertical slices delivered value incrementally and caught integration issues early.

### Checkpoints Are Non-Negotiable

Every phase checkpoint required human review before proceeding. This caught issues that automated checks missed (architecture violations, unclear naming, missing edge cases). The 5-axis review (Correctness, Readability, Architecture, Security, Performance) became second nature.

### Git Discipline Pays Off

Conventional Commits, descriptive branch names, and atomic commits made the git history readable. `git log --oneline` tells the project story. This is invaluable for code review and future debugging.

---

## Key Takeaways

1. **Start with the domain, not the database.** DDD entities and interfaces came first; infrastructure followed.
2. **Tests are design tools, not just quality gates.** Writing tests first forced cleaner interfaces and better naming.
3. **Partial processing is a feature, not an edge case.** Users uploading 1000 rows expect 999 to succeed even if 1 fails.
4. **Documentation is a feature.** The README, API reference, and contributing guide are what users see first.
5. **Ship Docker-ready from day one.** The multi-stage Dockerfile and docker-compose setup were trivial because the architecture was clean.

---

## Appendix: Phase Timeline

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| P1 | 1 day | Directory structure, configs, linters |
| P2 | 2 days | JWT auth, `/token` endpoint, health check |
| P3 | 1 day | Product entity + repository |
| P4 | 3 days | Customer/Order entities, `/upload` endpoint |
| P5 | 1 day | `/export` endpoint (JSON/CSV) |
| P6 | 2 days | 279 tests, 97.24% coverage |
| P7 | 1 day | Docker prod, CI/CD, rate limiting |
| P8 | 1 day | Documentation, API reference, retrospective |
