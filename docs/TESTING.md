# Testing Strategy

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## Three-Phase Testing Strategy

| Phase | Test Type | Objective | Tools | Min Coverage |
|-------|-----------|-----------|-------|-------------|
| **Unit** | Functions and classes | Validate isolated logic (e.g., validation, services) | `pytest`, `pytest-mock` | 90% |
| **Integration** | Module interaction | Validate complete flows (e.g., `/upload` → validation → persistence) | `pytest`, `TestClient` | 80% |
| **E2E** | User flows | Validate the API as a whole (e.g., auth + `/upload` + `/export`) | `pytest`, `httpx` | 70% |

---

## Frameworks & Fixtures

### Frameworks
- **Unit tests:** `pytest` + `pytest-mock`
- **Integration tests:** FastAPI `TestClient`
- **E2E tests:** `httpx` (for real HTTP requests)
- **Coverage:** `pytest-cov`

### Fixtures (`tests/conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_db

@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(test_db_session):
    def override_get_db():
        try:
            yield test_db_session
        finally:
            test_db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

---

## Test Examples

### Unit Test — Pydantic Validation

```python
# tests/unit/test_validation.py
from pydantic import ValidationError
import pytest
from app.schemas.order import OrderCreateSchema

def test_order_validation_positive_price():
    with pytest.raises(ValidationError) as exc_info:
        OrderCreateSchema(
            customer_id=1,
            items=[{"product_id": 1, "quantity": 2, "price": -10.0}]
        )
    assert "price" in str(exc_info.value)
    assert "must be greater than 0" in str(exc_info.value)
```

### Integration Test — `/upload`

```python
# tests/integration/test_upload.py
def test_upload_valid_order(client, test_db_session):
    data = {
        "orders": [
            {
                "customer_id": 1,
                "items": [{"product_id": 1, "quantity": 2, "price": 10.0}]
            }
        ]
    }
    response = client.post("/upload", json=data)
    assert response.status_code == 200
    assert "success" in response.json()
```

### E2E Test — Full Flow

```python
# tests/e2e/test_api.py
def test_full_flow(client):
    # 1. Login to get token
    login_data = {"username": "testuser", "password": "testpass"}
    login_response = client.post("/token", data=login_data)
    token = login_response.json()["access_token"]

    # 2. Upload with token
    headers = {"Authorization": f"Bearer {token}"}
    upload_data = {"orders": [{"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]}]}
    upload_response = client.post("/upload", json=upload_data, headers=headers)
    assert upload_response.status_code == 200

    # 3. Export
    export_response = client.get("/export", headers=headers)
    assert export_response.status_code == 200
    assert len(export_response.json()["orders"]) == 1
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
@pytest.fixture
def mock_current_user():
    return {"username": "testuser", "id": 1}

def test_upload_endpoint(client, mock_current_user, mocker):
    mocker.patch(
        "app.api.endpoints.upload.get_current_user",
        return_value=mock_current_user
    )
    response = client.post("/upload", json={"orders": []})
    assert response.status_code == 200
```