# Testing Strategy

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## Three-Phase Testing Strategy

| Phase | Test Type | Objective | Tools | Min Coverage |
|-------|-----------|-----------|-------|-------------|
| **Unit** | Functions and classes | Validate isolated logic (e.g., validation, services) | `pytest`, `pytest-mock`, `pytest-asyncio` | 90% |
| **Integration** | Module interaction | Validate complete flows (e.g., `/upload` → validation → persistence) | `pytest`, `httpx.AsyncClient`, `pytest-asyncio` | 80% |
| **E2E** | User flows | Validate the API as a whole (e.g., auth + `/upload` + `/export`) | `pytest`, `httpx.AsyncClient`, `pytest-asyncio` | 70% |

---

## Frameworks & Fixtures

### Frameworks
- **Unit tests:** `pytest` + `pytest-mock` + `pytest-asyncio`
- **Integration tests:** `httpx.AsyncClient` with `ASGITransport` (async FastAPI test client)
- **E2E tests:** `httpx.AsyncClient` (for real HTTP requests)
- **Coverage:** `pytest-cov`
- **Async DB testing:** `aiosqlite` (in-memory SQLite for async tests)

### Async Test Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
python_files = "test_*.py"
addopts = "--verbose --cov=app --cov-report=term-missing"
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
omit = ["app/__init__.py", "app/*/__init__.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false
```

### Fixtures (`tests/conftest.py`)

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_db

# Async SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create an async SQLite engine for the test session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine):
    """Provide an async database session with rollback after each test."""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_db_session):
    """Provide an async HTTP test client with DB dependency override."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(test_db_session):
    """Create a test user in the database and return credentials."""
    from app.infrastructure.auth.password_service import PasswordService
    from app.infrastructure.database.models.user import UserModel

    hashed_password = PasswordService.hash_password("testpassword123")
    user = UserModel(username="testuser", hashed_password=hashed_password)
    test_db_session.add(user)
    await test_db_session.flush()

    return {
        "username": "testuser",
        "password": "testpassword123",
        "user_id": user.id,
    }
```

---

## Test Examples

### Unit Test — Pydantic Validation (Synchronous)

```python
# tests/unit/test_validation.py
from pydantic import ValidationError
import pytest
from app.schemas.order import OrderCreateSchema


def test_order_validation_positive_price():
    """Price must be greater than 0."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreateSchema(
            customer_id=1,
            items=[{"product_id": 1, "quantity": 2, "price": -10.0}],
        )
    assert "price" in str(exc_info.value)
    assert "must be greater than 0" in str(exc_info.value)
```

### Unit Test — JWT Service (Synchronous)

```python
# tests/unit/test_jwt_service.py
import pytest
from app.infrastructure.auth.jwt_service import JWTService
from app.schemas.user import TokenDataSchema


def test_create_and_verify_token():
    """Token created by JWTService should be verifiable."""
    token = JWTService.create_token(username="testuser")
    token_data = JWTService.verify_token(token)
    assert token_data is not None
    assert token_data.username == "testuser"


def test_verify_expired_token():
    """Expired tokens should return None."""
    token = JWTService.create_token(username="testuser", expires_delta=timedelta(seconds=-1))
    result = JWTService.verify_token(token)
    assert result is None


def test_verify_invalid_token():
    """Invalid tokens should return None."""
    result = JWTService.verify_token("invalid.token.here")
    assert result is None
```

### Unit Test — Password Service (Synchronous)

```python
# tests/unit/test_password_service.py
from app.infrastructure.auth.password_service import PasswordService


def test_hash_and_verify_password():
    """Hashed password should verify against the original."""
    hashed = PasswordService.hash_password("mypassword123")
    assert PasswordService.verify_password("mypassword123", hashed) is True


def test_verify_wrong_password():
    """Wrong password should not verify."""
    hashed = PasswordService.hash_password("mypassword123")
    assert PasswordService.verify_password("wrongpassword", hashed) is False
```

### Integration Test — POST /token (Async)

```python
# tests/integration/test_auth_endpoint.py
import pytest


@pytest.mark.asyncio
async def test_login_valid_credentials(client, test_user):
    """Valid credentials should return a JWT token."""
    response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_user):
    """Invalid credentials should return 401."""
    response = await client.post(
        "/token",
        data={"username": test_user["username"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check(client):
    """GET / should return health check response."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
```

### Integration Test — `/upload` (Async)

```python
# tests/integration/test_upload.py
import pytest


@pytest.mark.asyncio
async def test_upload_valid_order(client, test_db_session, test_user):
    """Upload valid order data should return 200."""
    token_response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "orders": [
            {
                "customer_id": 1,
                "items": [{"product_id": 1, "quantity": 2, "price": 10.0}],
            }
        ]
    }
    response = await client.post("/upload", json=data, headers=headers)
    assert response.status_code == 200
    assert "success" in response.json()
```

### E2E Test — Full Flow (Async)

```python
# tests/e2e/test_full_flow.py
import pytest


@pytest.mark.asyncio
async def test_full_flow(client, test_user):
    """Full E2E flow: login → upload → export."""
    # 1. Login to get token
    login_response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload with token
    upload_data = {
        "orders": [
            {"customer_id": 1, "items": [{"product_id": 1, "quantity": 1, "price": 10.0}]}
        ]
    }
    upload_response = await client.post("/upload", json=upload_data, headers=headers)
    assert upload_response.status_code == 200

    # 3. Export
    export_response = await client.get("/export", headers=headers)
    assert export_response.status_code == 200
    assert len(export_response.json()["orders"]) >= 1
```

---

## Quality Metrics

| Metric | Tool | Target | Acceptable Limit |
|--------|------|--------|-----------------|
| Code coverage | `pytest-cov` | % of code covered by tests | ≥ 80% |
| Cyclomatic complexity | `radon` | Complexity per function | ≤ 10 |
| Technical debt | `sonarcloud` (optional) | Code issues | 0 critical |
| Code duplication | `ruff` | % of duplicated code | ≤ 5% |

---

## Mocking & Isolation Strategy

### Repositories
Use `pytest-mock` to mock DB calls:

```python
def test_upload_service(mocker):
    mock_repo = mocker.MagicMock()
    mock_repo.insert_order.return_value = Order(id=1)
    service = OrderService(repository=mock_repo)
    result = service.create_order(order_data)
    assert result.id == 1
    mock_repo.insert_order.assert_called_once()
```

### External Services
If external APIs are integrated in the future, use `httpx.MockTransport`.

### Authentication
Mock `get_current_user` in endpoint tests:

```python
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_upload_endpoint_with_mock_auth(client, mocker):
    """Test upload endpoint with mocked authentication."""
    mock_user = UserResponseSchema(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        username="testuser",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    mocker.patch(
        "app.infrastructure.auth.dependencies.get_current_user",
        new_callable=AsyncMock,
        return_value=mock_user,
    )
    response = await client.post("/upload", json={"orders": []})
    # ... assertions
```

### Async Database Isolation
Each test gets a fresh database session with automatic rollback:

```python
@pytest.fixture(scope="function")
async def test_db_session(test_db_engine):
    """Provide an async database session with rollback after each test."""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
```

This ensures test isolation — no test data leaks between test runs.