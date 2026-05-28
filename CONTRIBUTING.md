# Contributing

Thank you for considering contributing to this project. This guide covers everything you need to get started.

---

## Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16 (or Docker)
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Fisherk2/api-csv-bulk-import.git
cd api-csv-bulk-import

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Start PostgreSQL (via Docker)
docker-compose up -d db

# Apply migrations
alembic upgrade head

# Run the API
uvicorn app.main:app --reload

# Run tests
pytest --cov=app
```

---

## Code Standards

### Style

- **Formatter/Linter:** `ruff` (line length 88, double quotes)
- **Type checker:** `mypy` (strict mode)
- **Docstrings:** Google format
- **Naming:** See [docs/CODE-STYLE.md](docs/CODE-STYLE.md)

### File Rules

- Max 300 lines per file (except `__init__.py`)
- One class/function per file when practical
- Tests mirror source structure: `app/core/services/order_service.py` → `tests/unit/test_order_service.py`

### Architecture

- Domain layer (`app/core/`) has **zero external dependencies**
- Repository interfaces use ABC with `@abstractmethod`
- Services depend on interfaces, not implementations (Dependency Inversion)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture guide.

---

## Pre-Commit Checklist

Every commit must pass:

```bash
ruff check .          # Linting
ruff format .         # Formatting
mypy .                # Type checking
pytest                # Tests
```

All four must pass before committing. No exceptions.

---

## Testing

### Running Tests

```bash
# All tests with coverage
pytest --cov=app

# Specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/           # End-to-end tests

# Single test file
pytest tests/unit/test_order_service.py -v

# Single test
pytest tests/unit/test_order_service.py::test_upload_orders -v
```

### Writing Tests

- Follow the Arrange-Act-Assert pattern
- Use descriptive test names: `test_upload_orders_returns_200_when_all_valid`
- Prefer real implementations over mocks (see [docs/TESTING.md](docs/TESTING.md))
- New features require tests alongside code
- Bug fixes require a reproduction test before the fix

---

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feat/T27-description    # Feature
git checkout -b fix/T12-description     # Bug fix
git checkout -b docs/T28-description    # Documentation
```

### 2. Make Changes

- Follow the code standards above
- Write tests for new functionality
- Update documentation if needed

### 3. Verify

```bash
ruff check . && ruff format . && mypy . && pytest
```

All must pass.

### 4. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build process, CI, dependencies |
| `perf` | Performance improvement |

**Examples:**

```
feat: add CSV upload endpoint with partial processing
fix: correct FK validation in order batch insert
docs: update API reference with curl examples
test: add integration tests for /export pagination
refactor: extract _get_order_service helper
```

### 5. Push and Create PR

```bash
git push origin feat/T27-description
```

PR description should include:
- What changed and why
- Related task/issue number
- Testing done

### 6. Review

- All CI checks must pass
- At least one review before merge
- Squash merge preferred

---

## Commit Message Format

```
feat(T08): add Product entity and schemas

Add Product dataclass with UUID, name, price, and stock fields.
Includes ProductCreateSchema with validation constraints.

Closes #T08
```

**Format:** `<type>(<scope>): <description>`

- **type:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`
- **scope:** Task number or component (optional)
- **description:** Imperative mood, lowercase, no period

---

## Branch Naming

| Pattern | Example |
|---------|---------|
| `feat/T{NN}-description` | `feat/T08-product-entity` |
| `fix/T{NN}-description` | `fix/T13-order-fk-validation` |
| `docs/T{NN}-description` | `docs/T27-readme-rewrite` |

---

## Project Structure

```
app/
├── core/              # Domain entities, interfaces, services
├── infrastructure/    # DB models, repos, auth, rate limiting
├── schemas/           # Pydantic request/response schemas
├── utils/             # CSV/JSON parsers, file utilities
├── config.py          # Settings via pydantic-settings
└── main.py            # App factory

tests/
├── unit/              # Isolated tests (no I/O)
├── integration/       # Tests with DB/external deps
└── e2e/               # Full flow tests (ASGI + Docker)
```

---

## Questions?

Open an issue or refer to:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Architecture decisions
- [docs/CODE-STYLE.md](docs/CODE-STYLE.md) — Code conventions
- [docs/TESTING.md](docs/TESTING.md) — Testing strategy
- [SPEC.md](SPEC.md) — Project specification
