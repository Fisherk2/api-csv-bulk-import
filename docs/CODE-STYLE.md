# Code Style & Conventions

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## SOLID Principles

| Principle | Application | Example |
|-----------|-------------|---------|
| **Single Responsibility** | Each class/module has one responsibility | `OrderRepository` only handles DB operations for `Order` |
| **Open/Closed** | Entities and services open for extension, closed for modification | `ValidationService` can be extended with new rules without modifying existing code |
| **Liskov Substitution** | Repository implementations can substitute their interfaces | `OrderRepository` (SQLAlchemy) implements `IOrderRepository` |
| **Interface Segregation** | Repository interfaces are specific to each entity | `IOrderRepository` only has `Order`-related methods |
| **Dependency Inversion** | Use cases depend on abstractions (interfaces), not concrete implementations | `UploadUseCase` depends on `IOrderRepository`, not `OrderRepository` |

---

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Pydantic Classes** | PascalCase, `Schema` suffix | `OrderCreateSchema` |
| **SQLAlchemy Classes** | PascalCase, `Model` suffix | `OrderModel` |
| **DDD Entities** | PascalCase | `Order`, `Product` |
| **Repositories** | PascalCase, `Repository` suffix | `OrderRepository` |
| **Services** | PascalCase, `Service` suffix | `OrderService` |
| **Use Cases** | PascalCase, `UseCase` suffix | `UploadOrderUseCase` |
| **Endpoints** | snake_case | `upload_order`, `export_orders` |
| **Variables** | snake_case | `order_id`, `customer_name` |
| **Functions** | snake_case | `validate_order`, `parse_csv` |
| **Files** | snake_case | `order_repository.py`, `upload.py` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_BATCH_SIZE = 1000` |

---

## File Structure Rules

- **Rule 1:** Each file must have a **maximum of 300 lines** (exception: `__init__.py` for exports).
- **Rule 2:** Test files must mirror source code structure (e.g., `tests/unit/test_order_service.py`).
- **Rule 3:** Use `__init__.py` to expose public symbols:

```python
from .order import Order
from .product import Product
__all__ = ["Order", "Product"]
```

---

## Pre-Commit Checklist

All commits must pass these checks:

- [ ] **Linter:** `ruff check .` (no errors)
- [ ] **Formatter:** `ruff format .` (code formatted)
- [ ] **Type checker:** `mypy .` (no type errors)
- [ ] **Tests:** `pytest` (all tests pass)
- [ ] **Migrations:** `alembic revision --autogenerate` (if model changes)
- [ ] **Documentation:** Update `README.md` and docstrings if needed

### Tool Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
python_files = "test_*.py"
addopts = "--verbose --cov=app --cov-report=term-missing"
```

---

## Prohibited Practices

| Practice | Reason | Alternative |
|----------|--------|-------------|
| Hardcoding secrets | Security risk | Environment variables |
| Using `print` for debugging | Unstructured, hard to filter | `logging` with JSON format |
| Ignoring exceptions | Can leave app in inconsistent state | Handle all exceptions explicitly |
| Long transactions | Blocks DB, reduces performance | Split into smaller transactions |
| Raw SQL in code | SQL injection risk | Use SQLAlchemy ORM or Core |
| Validation in endpoint | Couples business logic to API layer | Validate in `ValidationService` |
| Returning sensitive data in errors | Information exposure risk | Generic messages + internal logs |
| Using `any` as type | Loses static typing | Use specific types or `Typing.Any` |
| Modifying global state | Makes testing and debugging hard | Use dependency injection |
| Temporal coupling | Makes reuse and testing hard | Use **Repository** or **Service Layer** patterns |