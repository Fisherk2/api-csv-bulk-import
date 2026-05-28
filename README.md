# Bulk Import/Export API with Strict Validation

[![CI](https://github.com/Fisherk2/api-csv-bulk-import/actions/workflows/ci.yml/badge.svg)](https://github.com/Fisherk2/api-csv-bulk-import/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-97.24%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> REST API built with FastAPI for bulk import/export of relational data (orders, products, customers) with **strict Pydantic validation**, **partial batch processing**, **JWT authentication**, and **RFC 7807 error reporting**.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Framework | FastAPI | 0.115+ |
| Validation | Pydantic | 2.x |
| ORM | SQLAlchemy (async) | 2.x |
| Database | PostgreSQL | 16 |
| Auth | JWT (OAuth2 Password Flow) | python-jose |
| Testing | pytest + pytest-cov | — |
| Linting | ruff | — |
| Type checking | mypy | — |
| Containers | Docker + Docker Compose | — |

---

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/Fisherk2/api-csv-bulk-import.git
cd api-csv-bulk-import

cp .env.example .env
# Edit .env — set DB_PASSWORD and SECRET_KEY

docker-compose up -d
# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL (via Docker or local)
docker-compose up -d db

# Apply migrations
alembic upgrade head

# Run the API
uvicorn app.main:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Health check | No |
| `POST` | `/token` | Obtain JWT token | No |
| `POST` | `/upload` | Import orders (CSV or JSON) | Yes |
| `GET` | `/export` | Export orders (CSV or JSON) | Yes |

### Authentication

```bash
# Get a token
curl -X POST http://localhost:8000/token \
  -d "username=admin@example.com&password=secret123"

# Use the token in subsequent requests
curl http://localhost:8000/export \
  -H "Authorization: Bearer <token>"
```

### Upload (CSV/JSON)

```bash
# JSON upload
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [{
      "customer_email": "alice@example.com",
      "customer_name": "Alice Johnson",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "quantity": 2,
      "price": 29.99,
      "status": "pending"
    }]
  }'

# CSV upload
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@orders.csv"
```

### Export (CSV/JSON)

```bash
# JSON export (default)
curl http://localhost:8000/export \
  -H "Authorization: Bearer <token>"

# CSV export
curl "http://localhost:8000/export?format=csv" \
  -H "Authorization: Bearer <token>"

# Pagination
curl "http://localhost:8000/export?skip=0&limit=50" \
  -H "Authorization: Bearer <token>"
```

---

## Testing

```bash
# Run all tests with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/           # End-to-end tests

# Lint and type check
ruff check .
mypy .
```

---

## Deployment

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This starts:
- **API** — uvicorn with 4 workers
- **PostgreSQL 16** — with persistent volume
- **Nginx** — reverse proxy with security headers on port 80

### Environment Variables

See [`.env.example`](.env.example) for all configurable options. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PASSWORD` | `change-me` | PostgreSQL password |
| `SECRET_KEY` | `change-me-...` | JWT signing key |
| `MAX_BATCH_SIZE` | `1000` | Max rows per upload |
| `MAX_FILE_SIZE_MB` | `10` | Max upload file size |
| `RATE_LIMIT_PER_MINUTE` | `100` | Global rate limit (0 = disabled) |
| `TOKEN_RATE_LIMIT` | `20` | `/token` rate limit |
| `UPLOAD_RATE_LIMIT` | `30` | `/upload` rate limit |
| `EXPORT_RATE_LIMIT` | `100` | `/export` rate limit |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token TTL |

---

## Architecture

Domain-Driven Design (DDD) with vertical slices:

```
app/
├── core/              # Domain entities, repository interfaces, services (zero external deps)
│   ├── entities/      # Order, Product, Customer, User (pure dataclasses)
│   ├── repositories/  # ABC interfaces (IOrderRepository, etc.)
│   └── services/      # OrderService, ExportService (business logic)
├── infrastructure/    # DB models, repository implementations, auth, rate limiting
│   ├── database/      # SQLAlchemy models, Base, session factory
│   ├── repositories/  # Concrete repos (OrderRepository, etc.)
│   ├── auth/          # JWT, password hashing, dependencies
│   ├── api/           # FastAPI routers and endpoints
│   └── rate_limiter.py
├── schemas/           # Pydantic request/response schemas
├── utils/             # CSV/JSON parsers, file utilities
└── main.py            # App factory, middleware, CORS
```

**Key patterns:**
- Repository pattern with ABC interfaces
- Service Layer with dependency injection
- Partial batch processing (valid rows succeed, invalid rows reported)
- RFC 7807 Problem Details error format

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture guide.

---

## Project Metrics

| Metric | Value |
|--------|-------|
| Source files | 53 |
| Test files | 40 |
| Source LOC | 2,622 |
| Test LOC | 5,072 |
| Test coverage | 97.24% |
| Lint issues (ruff) | 0 |
| Type errors (mypy) | 0 |

---

## Documentation

- [SPEC.md](SPEC.md) — Project specification
- [WORKFLOW.md](WORKFLOW.md) — Implementation tracking and phase progress
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Patterns, diagrams, folder structure
- [docs/DOMAIN.md](docs/DOMAIN.md) — Entities, requirements, system boundaries
- [docs/CODE-STYLE.md](docs/CODE-STYLE.md) — Naming, SOLID, file rules
- [docs/TESTING.md](docs/TESTING.md) — Testing strategy, frameworks, examples
- [docs/SECURITY.md](docs/SECURITY.md) — Validation, errors, rate limiting, secrets
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) — API reference with curl examples
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines

---

## License

MIT
