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
make install

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Start PostgreSQL + API (via Docker)
make docker-up

# Apply migrations (auto-run on container start)
# or manually: make migrate message="your description"

# Run tests with coverage
make test-cov
```

---

## Makefile Workflow

This project includes a [Makefile](Makefile) with targets for the most common development tasks. Use `make` instead of typing raw commands:

```bash
make help           # List all available targets
make install        # Install dependencies
make lint           # Lint with ruff
make format         # Auto-format with ruff
make type-check     # Type check with mypy (source code only)
make test           # Run tests (quick)
make test-cov       # Run tests with coverage report
make dev            # Start dev server with auto-reload (HOST=0.0.0.0 PORT=8000)
make run            # Start production server (no reload)
make docker-up      # Start Docker stack (api + db)
make docker-down    # Stop Docker stack
make docker-logs    # Follow Docker logs
make clean          # Remove cache files and artifacts
```

**Customize:** Override defaults with variables:
```bash
make dev HOST=127.0.0.1 PORT=9000
make migrate message="add orders table"
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
make lint             # Linting (ruff check .)
make format           # Formatting (ruff format .)
make type-check       # Type checking (mypy app/)
make test             # Tests (pytest)
```

Alternatively, use the raw commands:

```bash
ruff check . && ruff format . && mypy app/ && pytest
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
make lint && make format && make type-check && make test
```

Or the equivalent raw commands:

```bash
ruff check . && ruff format . && mypy app/ && pytest
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
