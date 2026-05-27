# P7: Deployment — Implementation Spec

**Phase:** P7 — Deployment
**Status:** 🔵 Ready for Implementation
**Depends on:** P1 (Foundation) ✅, P2 (Auth Slice) ✅, P4 (Upload Slice) ✅, P5 (Export Slice) ✅, P6 (Testing) ✅
**Blocks:** P8 (Closure)

---

## Objective

Deliver a **containerized, production-ready deployment** of the Bulk Import/Export API with automated CI/CD quality gates. This phase transforms the project from "runs locally with `make dev`" to "starts with `docker-compose up`" with a multi-stage Dockerfile, Nginx reverse proxy (production), and a GitHub Actions CI pipeline that enforces all quality checks on every push and pull request.

**Target user:** Developer evaluating backend architecture skills (portfolio project). The Docker setup demonstrates containerization expertise, while the CI pipeline demonstrates DevOps automation competence.

**Success criteria:**
1. `docker-compose up` starts the full stack (API + PostgreSQL) and API responds on port 8000
2. `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d` starts production stack (API + PostgreSQL + Nginx) with all services healthy
3. Multi-stage `Dockerfile` produces an image under 300 MB with no build tools in the final stage
4. `.dockerignore` excludes unnecessary files (`.git`, `__pycache__`, `.venv`, `tests/`, etc.)
5. Rate limiting is active in production — per-IP limits enforced via `slowapi`
6. CI pipeline on GitHub Actions runs on every push and PR: lint → type-check → test → coverage check
7. CI uses PostgreSQL 16 service container for integration tests
8. CI fails if coverage < 80%
9. CI caches pip dependencies
10. `ruff check .` and `mypy .` pass with zero errors (no regression from P6)
11. All 261 tests continue to pass in CI with PostgreSQL (no test regressions)
12. Domain layer (`app/core/`) has zero external dependencies

---

## Architectural Decisions

### AD-P7-01: Multi-Stage Dockerfile — Build + Production

| Decision | Rationale |
|----------|-----------|
| **Build stage:** `python:3.12-slim` with full dev dependencies. Installs all packages from `requirements.txt`, copies source. | Slim image balances size (~150 MB base) vs compatibility (apt-get available for build tools if needed). Build stage has dev deps for potential future build steps. |
| **Production stage:** `python:3.12-slim` with only production dependencies. Copies installed packages and app source from build stage. Runs as non-root `appuser`. Uses `uvicorn` directly as the web server. | Separates build and runtime concerns. No dev tools (ruff, mypy, pytest, httpx) in the final image — reduces attack surface and image size. Non-root user follows security best practices from `skills/docker-optimize`. |
| **Uvicorn configuration:** `--host 0.0.0.0 --port 8000 --workers 4 --no-access-log` in production. | 4 workers for concurrency on multi-core systems. `--no-access-log` defers access logging to Nginx in prod. |

### AD-P7-02: Production Stack — API + PostgreSQL + Nginx

| Decision | Rationale |
|----------|-----------|
| **Nginx as reverse proxy** in front of Uvicorn. Handles: static file serving (if needed), request buffering, connection keep-alive, access logging, client max body size enforcement, and optional SSL termination. | Demonstrates realistic production infrastructure. Separates concerns: Nginx handles HTTP-level concerns (buffering, logging, rate limiting at edge), Uvicorn focuses on ASGI. |
| **Nginx configuration:** Listens on port 80 (HTTP). Proxies `/` to API on port 8000. Sets `client_max_body_size 10m` (matches `MAX_FILE_SIZE_MB`). Adds security headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`). | Production-grade defaults. Security headers add defense-in-depth. Body size limit at edge complements application-level validation. |
| **No SSL in MVP:** Nginx serves HTTP only. SSL termination (via Caddy or Let's Encrypt) is documented as future work. | Avoids certificate management complexity. SSL is easy to add later by swapping Nginx for Caddy or adding certbot. |

### AD-P7-03: Docker Compose — Dev vs Prod Separation

| Decision | Rationale |
|----------|-----------|
| `docker-compose.yml` — base configuration. Defines `api` (build from Dockerfile), `db` (PostgreSQL 16 Alpine), volumes, and networks. `api` has `DEBUG=true`, `--reload`, mounts source code for hot-reload. Port 8000 exposed. | Developer-friendly: source code changes reflect immediately, debug logs visible. Matches P1 placeholder + extends it with API service. |
| `docker-compose.prod.yml` — production overrides. Overrides `api` command to `--workers 4 --no-access-log`, sets `DEBUG=false`, removes source mount, adds resource limits (CPU: 1.0, memory: 512M). Adds `nginx` service (image: `nginx:1.27-alpine`). Health checks on all services. | Production concerns: no reload, no debug, resource limits prevent runaway containers, health checks enable orchestration. Override file composes with base file for DRY config. |

### AD-P7-04: Health Checks on All Services

| Decision | Rationale |
|----------|-----------|
| **API:** `curl -f http://localhost:8000/` — validates the app boots and responds. Interval: 30s, timeout: 10s, retries: 3. | Docker waits for health check before marking service as "healthy". Critical for orchestration, CI, and deployment scripts. |
| **PostgreSQL:** `pg_isready -U postgres` — already in placeholder. Interval: 5s, timeout: 5s, retries: 5. | Verifies PostgreSQL accepts connections before API starts. |
| **Nginx (prod):** `curl -f http://localhost:80/` — validates the reverse proxy passes through to API. Interval: 30s, timeout: 10s, retries: 3. | Ensures the full chain (Nginx → Uvicorn → API) is healthy. |

### AD-P7-05: Rate Limiting with slowapi

| Decision | Rationale |
|----------|-----------|
| Add `slowapi` middleware to FastAPI app in `main.py`. Default limit: 100 req/min per IP (configurable via `RATE_LIMIT_PER_MINUTE` env var). Apply globally with `@limiter.limit` decorator on auth endpoint (stricter: 20 req/min). | `slowapi` is already in `requirements.txt` and `pyproject.toml`. Implementing it now closes the P4 deferred decision (AD-P4-08). Demonstrates API security awareness. |
| Custom key function `get_real_ip()` reads `X-Forwarded-For` header (set by Nginx) instead of using `get_remote_address`. Falls back to `request.client.host` for direct connections. | Without this, all requests behind Nginx would share the proxy's IP, making rate limiting useless in production. The custom function extracts the real client IP from the header chain. |
| Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) added to responses. | Standard headers let clients self-regulate. |
| Rate limiting disabled in tests via `RATE_LIMIT_PER_MINUTE=0`. | Prevents flaky tests from hitting rate limits. |

### AD-P7-06: GitHub Actions CI with PostgreSQL Service Container

| Decision | Rationale |
|----------|-----------|
| **CI workflow** triggers on `push` to `main`/`feature/*` branches and `pull_request` to `main`. Jobs: `lint` (ruff), `type-check` (mypy), `test` (pytest with PostgreSQL). Parallel execution of lint + type-check. | Follows `skills/ci-cd-and-automation` quality gate pipeline. Parallel jobs reduce CI time. |
| **PostgreSQL 16 service container** for integration tests. Database: `ci_test_db`, user: `ci_user`, password via GitHub Secrets `CI_DB_PASSWORD` with hardcoded fallback for public repos. Health check: `pg_isready`. | Real PostgreSQL validates asyncpg behavior (not SQLite). Service containers are native to GitHub Actions — no Docker Compose overhead. |
| **Pip caching** via `actions/setup-python@v5` with `cache: 'pip'`. | Reduces CI time by reusing downloaded packages. |
| **Coverage gate:** `pytest --cov=app --cov-report=term-missing --cov-fail-under=80`. | CI fails if coverage drops below 80%, enforcing quality threshold. |

### AD-P7-07: .dockerignore File

| Decision | Rationale |
|----------|-----------|
| Exclude: `.git`, `__pycache__/`, `*.pyc`, `.venv/`, `.env`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `htmlcov/`, `tests/`, `*.md` (except README.md?), `.github/`, `specs/`, `tasks/`, `.pre-commit-config.yaml`. | Minimizes Docker build context. Excluding tests from image reduces size. Excluding `.git` prevents accidentally shipping Git history. |

---

## Current State Analysis

### What Already Exists

| Component | Status | Notes |
|-----------|--------|-------|
| `Dockerfile` | Placeholder (1 line) | Needs full multi-stage definition |
| `docker-compose.yml` | Placeholder (PostgreSQL only) | Has `db` service with `postgres:16-alpine`, health check, volume. Needs `api` service added. |
| `.dockerignore` | Missing | Must be created |
| `docker-compose.prod.yml` | Missing | Must be created |
| `.github/workflows/ci.yml` | Missing | Must be created |
| `slowapi` in `requirements.txt` | Present but unused | Must be integrated into `main.py` |
| App code (`app/`) | Complete | All endpoints, services, repos, schemas, models, DB config |
| Tests (`tests/`) | Complete (261 tests, 96.98%) | Must pass in CI with PostgreSQL |
| `alembic.ini` + `migrations/` | Complete | Migrations must run before API starts |
| `.env.example` | Complete | Has `RATE_LIMIT_PER_MINUTE=100`, `DEBUG=false`, etc. |

### What Needs to Be Created or Modified

| File | Action | Scope |
|------|--------|-------|
| `Dockerfile` | Replace placeholder with multi-stage build | ~60 lines |
| `.dockerignore` | Create new | ~25 lines |
| `docker-compose.yml` | Add `api` service, networks, dependency ordering | +20 lines |
| `docker-compose.prod.yml` | Create new — overrides + Nginx + resource limits | ~70 lines |
| `nginx/nginx.conf` (or inline in compose) | Create Nginx configuration | ~35 lines |
| `.github/workflows/ci.yml` | Create new — lint + type-check + test | ~90 lines |
| `app/main.py` | Add slowapi middleware with custom `get_real_ip()` key function | +30 lines |
| `app/config.py` | No changes needed (already has `RATE_LIMIT_PER_MINUTE`) | — |
| `Makefile` | Add `docker-build`, `docker-up`, `docker-down`, `docker-logs` targets | +15 lines |
| `scripts/entrypoint.sh` | Create new | ~10 lines |

---

## Tasks

### Task 24: Docker Dev Setup (T24)

**Description:** Create multi-stage `Dockerfile`, `.dockerignore`, complete `docker-compose.yml` for development, entrypoint script, and `Makefile` Docker targets. Replace the placeholder files with production-quality container setup.

**Acceptance criteria:**
- [ ] `Dockerfile` has two stages: `build` and `production`
- [ ] Build stage installs all dependencies from `requirements.txt` globally (not `--user`)
- [ ] Production stage copies site-packages from `/usr/local/` (not `/root/.local`)
- [ ] Production stage runs as non-root user (`appuser`, UID 1000)
- [ ] Production stage uses `python:3.12-slim` base image
- [ ] Image size under 300 MB
- [ ] `.dockerignore` excludes `.git`, caches, tests, docs, and virtual environments
- [ ] `docker-compose.yml` defines `api` service (builds from Dockerfile) and `db` service (PostgreSQL 16 Alpine)
- [ ] `api` service depends on `db` with health check condition (`condition: service_healthy`)
- [ ] `api` service has health check (`curl -f http://localhost:8000/`)
- [ ] Development command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- [ ] Source code mounted as volume for hot-reload in dev
- [ ] `DEBUG=true` environment variable for dev
- [ ] Database migration runs on container startup via `scripts/entrypoint.sh`
- [ ] `Makefile` has `docker-build`, `docker-up`, `docker-down`, `docker-logs` targets

**Verification:**
- [ ] `docker-compose up -d` — both services start and are healthy
- [ ] `curl http://localhost:8000/` — returns `{"status": "ok", "version": "1.0.0"}`
- [ ] `docker-compose down` — clean shutdown
- [ ] `docker images api-csv-bulk-import` — image size < 300 MB
- [ ] `make docker-build && make docker-up && make docker-down` — all targets work

**Dependencies:** Task 3 (Linters), Task 17 (/upload endpoint)

**Files likely touched:**
- `Dockerfile` (replace placeholder — ~60 lines)
- `docker-compose.yml` (add api service — +20 lines)
- `.dockerignore` (new — ~25 lines)
- `scripts/entrypoint.sh` (new — startup script for migrations + uvicorn)
- `Makefile` (add Docker targets — +15 lines)

**Estimated scope:** Medium (5 files)

---

### Task 25: Rate Limiting Integration

**Description:** Integrate `slowapi` rate limiting middleware into the FastAPI application. Apply global rate limit (100 req/min) and stricter limit on `/token` endpoint (20 req/min). Use a custom key function that reads `X-Forwarded-For` for correct IP detection behind Nginx. Add rate limit headers to responses.

> **Note:** This task was not originally in the plan but was deferred from P4 (AD-P4-08) and confirmed by the user as part of P7 scope. It's a prerequisite for production readiness. The custom `get_real_ip()` function is critical because the default `get_remote_address` would report Nginx's IP instead of the real client IP.

**Acceptance criteria:**
- [ ] `slowapi` middleware added to FastAPI app in `main.py`
- [ ] Custom key function `get_real_ip()` reads `X-Forwarded-For` header (falls back to `request.client.host`)
- [ ] Global rate limit: 100 req/min per IP (configurable via `RATE_LIMIT_PER_MINUTE`)
- [ ] `/token` endpoint has stricter limit: 20 req/min via `@limiter.limit("20/minute")`
- [ ] `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers in all responses
- [ ] Rate limiting disabled when `RATE_LIMIT_PER_MINUTE=0` (for tests)
- [ ] `rate_limit_exceeded_handler` returns RFC 7807 error: HTTP 429 with `type: "about:blank"`, `title: "Too Many Requests"`
- [ ] All existing tests pass (rate limiting disabled via `RATE_LIMIT_PER_MINUTE=0`)
- [ ] At least 2 new tests: one verifies rate limit headers are present, one verifies 429 after exceeding limit

**Verification:**
- [ ] `curl -v http://localhost:8000/` — response includes `X-RateLimit-*` headers
- [ ] Rapid requests to `/token` — returns 429 after exceeding 20 req/min
- [ ] `pytest` — all 261 existing tests pass, 2+ new rate limit tests pass

**Dependencies:** Task 17 (/upload endpoint), Task 7 (Auth)

**Files likely touched:**
- `app/main.py` (add slowapi middleware, rate limit config, exception handler)
- `app/infrastructure/api/endpoints/auth.py` (add `@limiter.limit` decorator)
- `tests/unit/test_rate_limit.py` (new — rate limiting tests)
- `tests/conftest.py` (set `RATE_LIMIT_PER_MINUTE=0` for test env if not already)

**Estimated scope:** Small (2-3 files)

---

### Task 26: Docker Prod + CI/CD (T26)

**Description:** Create `docker-compose.prod.yml` with Nginx reverse proxy, resource limits, and production overrides. Create `.github/workflows/ci.yml` with automated quality gates (lint, type-check, test with PostgreSQL).

**Acceptance criteria:**
- [ ] `docker-compose.prod.yml` overrides `api` service: `DEBUG=false`, no source mount, `--workers 4 --no-access-log`
- [ ] `docker-compose.prod.yml` adds `nginx` service (image: `nginx:1.27-alpine`) as reverse proxy
- [ ] Nginx proxies requests to API on port 8000, handles `client_max_body_size 10m`
- [ ] Nginx adds security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`
- [ ] Resource limits on all services: API (CPU: 1.0, memory: 512M), DB (CPU: 1.0, memory: 512M), Nginx (CPU: 0.5, memory: 128M)
- [ ] CI workflow triggers on: `push` to `main` and `feature/*` branches, `pull_request` to `main`
- [ ] CI job `lint`: `ruff check .` with Python 3.12
- [ ] CI job `type-check`: `mypy .` with Python 3.12
- [ ] CI job `test`: `pytest --cov=app --cov-fail-under=80` with PostgreSQL 16 service container
- [ ] CI uses `actions/setup-python@v5` with `cache: 'pip'`
- [ ] CI fails if coverage < 80%
- [ ] CI jobs `lint` and `type-check` run in parallel, `test` runs after both pass
- [ ] Database migrations run before tests in CI (`alembic upgrade head`)

**Verification:**
- [ ] `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d` — all 3 services healthy
- [ ] `curl http://localhost:80/` — returns health check response via Nginx
- [ ] `curl -I http://localhost:80/` — includes security headers
- [ ] CI workflow YAML is valid (manual review against GitHub Actions schema)
- [ ] Push to `feature/*` branch triggers CI workflow (verify on first PR)
- [ ] CI passes all 3 jobs (lint ✅, type-check ✅, test ✅)

**Dependencies:** Task 24 (Docker dev setup), Task 25 (Rate limiting), Task 23 (E2E tests)

**Files likely touched:**
- `docker-compose.prod.yml` (new)
- `nginx/nginx.conf` (new)
- `.github/workflows/ci.yml` (new)

**Estimated scope:** Medium (3 files)

---

## Implementation Notes

### Dockerfile Structure

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS build
WORKDIR /app
# Install system deps needed for health checks and C extension compilation
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
# Install ALL deps globally (not --user) so they land in /usr/local/
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Stage 2: Production
FROM python:3.12-slim AS production
WORKDIR /app
# Copy Python packages from build stage (global install → /usr/local/)
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
# Copy app source and migrations
COPY --from=build /app/app ./app
COPY --from=build /app/migrations ./migrations
COPY --from=build /app/alembic.ini .
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Create non-root user and give access to /app
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/ || exit 1
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Entrypoint Script (`scripts/entrypoint.sh`)

```bash
#!/bin/bash
set -e
# Run database migrations
alembic upgrade head
# Execute the CMD (uvicorn)
exec "$@"
```

This ensures migrations run before the API starts. In docker-compose, the `api` service waits for `db` to be healthy before starting, so the migration has a running PostgreSQL to target.

### Nginx Configuration (`nginx/nginx.conf`)

```nginx
server {
    listen 80;
    server_name localhost;

    client_max_body_size 10m;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

### Docker Compose Architecture

**Development (`docker-compose.yml`):**
```yaml
services:
  db:        # PostgreSQL 16 Alpine (already exists)
  api:       # Builds from Dockerfile, dev mode (--reload, DEBUG=true)
```

**Production (`docker-compose.prod.yml`):**
```yaml
services:
  api:       # Override: production mode (--workers 4, DEBUG=false, resource limits)
  db:        # Add resource limits
  nginx:     # New: reverse proxy on port 80
```

### CI Pipeline Design

```
Push/PR to main/feature/*
    │
    ├── Job: lint (ruff check .)
    │   └── Parallel ─┐
    ├── Job: type-check (mypy .)   │
    │                      ────────┤
    │                              ▼
    └── Job: test (pytest --cov --cov-fail-under=80)
        ├── Service: postgres:16
        ├── alembic upgrade head
        └── pytest
```

### Rate Limiting Integration in `main.py`

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings


def get_real_ip(request: Request) -> str:
    """Extract real client IP behind Nginx reverse proxy.

    Uses X-Forwarded-For header when available (set by Nginx).
    Falls back to request.client.host for direct connections.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


limiter = Limiter(
    key_func=get_real_ip,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)


def create_app() -> FastAPI:
    app = FastAPI(...)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    # ...
    return app
```

The `/token` endpoint gets a stricter per-route limit:
```python
@router.post("/token")
@limiter.limit("20/minute")
async def login_for_access_token(...):
    ...
```

### Database for CI Tests

CI uses a PostgreSQL 16 service container. Migration must be applied before tests (`alembic upgrade head`). Test users are created by fixtures (as they are now). The `DATABASE_URL` environment variable points to the service container:

```yaml
env:
  DATABASE_URL: postgresql+asyncpg://ci_user:ci_password@localhost:5432/ci_test_db
  SYNC_DATABASE_URL: postgresql://ci_user:ci_password@localhost:5432/ci_test_db
```

---

## Checkpoint P7: Deployment Complete

- [x] `docker-compose up` — both `api` and `db` services healthy
- [x] `curl http://localhost:8000/` returns 200
- [x] `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d` — all 3 services (api, db, nginx) healthy
- [x] `curl http://localhost:80/` returns 200 via Nginx
- [x] Production security headers present on responses
- [x] Rate limiting active: 429 returned on exceeded limits
- [x] Multi-stage Dockerfile produces image < 300 MB, runs as non-root
- [x] `.dockerignore` present and effective
- [x] CI pipeline passes on push: lint ✅, type-check ✅, test ✅
- [x] CI fails when coverage < 80%
- [x] `ruff check .` and `mypy .` pass with zero errors
- [x] All 261 tests pass (no regressions)
- [x] Domain layer (`app/core/`) has zero external dependencies
- [x] **Human review completed** — 5 axes: Correctness ✅, Readability ✅, Architecture ✅, Security ✅, Performance ✅)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker build fails due to missing system deps for asyncpg/bcrypt compilation | High | `python:3.12-slim` has apt-get. Add `build-essential` temporarily in build stage if needed for C extensions. Test build early. |
| PostgreSQL service container in CI has different behavior than local dev | Medium | Use same PostgreSQL version (16) in both. Run migration in CI to validate schema compatibility. |
| Rate limiting breaks existing tests | Medium | Set `RATE_LIMIT_PER_MINUTE=0` (disabled) for test environment. Already in `.env.example`. Add to CI env as well. |
| Nginx configuration blocks valid requests | Low | Test with `curl` against production compose. Health check validates Nginx → API chain. |
| CI secrets exposure in public repo | Medium | Use GitHub Secrets for `CI_DB_PASSWORD`. Document that the password is non-sensitive (test-only DB destroyed after CI run). |
| Docker image exceeds 300 MB | Low | Multi-stage build + `--no-cache-dir` pip install + slim base image should keep it under 300 MB. Verify with `docker images` after build. |

---

## Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should the CI pipeline include Docker image build verification? | Resolved | **No** — CI only runs tests + quality checks. Docker build is manual or separate workflow (user decision). |
| 2 | Should the production stack include Redis for rate limiting persistence? | Resolved | **No** — slowapi uses in-memory storage (per-process). Sufficient for single-container deployment. Redis is future work for multi-replica deployments. |
| 3 | Should we add a `Makefile` target for Docker operations (`make docker-build`, `make docker-up`)? | Resolved | **Yes** — Add `docker-build`, `docker-up`, `docker-down`, `docker-logs` targets to Makefile as part of T24. `docker-compose` commands are straightforward but Make targets improve developer experience and document available operations. |
| 4 | Should the entrypoint script wait for PostgreSQL to be fully ready (beyond Docker health check)? | Resolved | **Yes** — Docker health check `condition: service_healthy` ensures PostgreSQL is ready before `api` starts. Entrypoint runs `alembic upgrade head` after that. |
