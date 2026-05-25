# API de Importación/Exportación Masiva con Validación Estricta

> REST API built with FastAPI for bulk import/export of relational data with strict Pydantic validation, partial processing, JWT authentication, and RFC 7807 error reporting.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Fisherk2/api-csv-bulk-import.git
cd api-csv-bulk-import

# Copy environment variables
cp .env.example .env

# Start the full stack
docker-compose up

# Run tests
pytest --cov=app
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115+ |
| Validation | Pydantic 2.x |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Auth | JWT (OAuth2 Password Flow) |
| Testing | pytest + pytest-cov + pytest-mock |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/token` | Obtain JWT token (OAuth2 Password Flow) |
| `POST` | `/upload` | Import data in CSV or JSON format |
| `GET` | `/export` | Export data in CSV or JSON format |

## Documentation

- [SPEC.md](SPEC.md) — Full project specification
- [WORKFLOW.md](WORKFLOW.md) — Implementation tracking and phase progress
- [AGENTS.md](AGENTS.md) — Quick reference and boundaries
- [Architecture & Design](docs/ARCHITECTURE.md) — Patterns, diagrams, folder structure
- [Domain & Requirements](docs/DOMAIN.md) — Entities, requirements, system boundaries
- [Code Style & Conventions](docs/CODE-STYLE.md) — Naming, SOLID, file rules
- [Testing Strategy](docs/TESTING.md) — Test phases, frameworks, fixtures, examples
- [Security & Error Handling](docs/SECURITY.md) — Validation, HTTP responses, rate limiting

## Status

🟡 **En Especificación** — Project is in the specification phase. No implementation yet.

## License

MIT