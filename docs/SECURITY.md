# Security & Error Handling

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## Input Validation & Sanitization

| Field | Validation | Sanitization |
|-------|-----------|-------------|
| **IDs** | Positive integer (`gt=0`) | None (PostgreSQL handles types) |
| **Names** | `str`, `min_length=1`, `max_length=100`, regex to prevent SQL injection | `strip()` to remove whitespace |
| **Emails** | `EmailStr` (Pydantic) | None (Pydantic validates format) |
| **Passwords** | `min_length=8`, `max_length=50`, at least 1 uppercase, 1 lowercase, 1 digit | Hashing with `bcrypt` |
| **Prices** | `float`, `gt=0`, `le=1000000` | Round to 2 decimals |
| **Quantity** | `int`, `gt=0`, `le=1000` | None |
| **CSV/JSON** | Validate structure (required headers in CSV, required fields in JSON) | Parse with safe libraries (`csv`, `json`) |

### Pydantic Sanitization Example

```python
from pydantic import BaseModel, field_validator

class ProductCreateSchema(BaseModel):
    name: str
    price: float

    @field_validator("name")
    def sanitize_name(cls, v: str) -> str:
        return v.strip()  # Remove leading/trailing whitespace
```

---

## Error Handling & HTTP Responses

| Error Type | Handling | HTTP Code | Response Format |
|-----------|---------|-----------|----------------|
| **Validation (Pydantic)** | Catch `ValidationError`, convert to RFC 7807 | 422 | RFC 7807 (Problem Details) |
| **Authentication (invalid JWT)** | `HTTPException(401, detail="Invalid token")` | 401 | RFC 7807 |
| **Authorization (no permissions)** | `HTTPException(403, detail="Not authorized")` | 403 | RFC 7807 |
| **Database (conflict)** | `IntegrityError` → `HTTPException(409, detail="Conflict")` | 409 | RFC 7807 |
| **Database (generic error)** | Log error, return `HTTPException(500, detail="Internal server error")` | 500 | RFC 7807 |
| **Invalid format (CSV/JSON)** | `HTTPException(400, detail="Invalid format")` | 400 | RFC 7807 |
| **Batch size exceeded** | `HTTPException(413, detail="Batch size exceeds limit")` | 413 | RFC 7807 |

### Fallback Strategies
- **DB Timeout:** Retry transaction **1 time** before failing (using `tenacity`).
- **CSV/JSON Parse Error:** Return error with **row number** and **problematic field**.

---

## Rate Limiting & Concurrency

| Scenario | Handling | Configuration |
|----------|---------|--------------|
| **DB Timeout** | Log error, rollback, re-raise | Exception propagates to FastAPI error handler |
| **Global Rate Limiting** | Limit per IP | `slowapi` middleware, configurable via `RATE_LIMIT_PER_MINUTE` |
| **Per-endpoint Rate Limiting** | `/token`: 20/min, `/upload`: 30/min, `/export`: 100/min | Configurable via `TOKEN_RATE_LIMIT`, `UPLOAD_RATE_LIMIT`, `EXPORT_RATE_LIMIT` |
| **Batch Size** | Maximum **1000 rows** per request | `MAX_BATCH_SIZE` setting |
| **File Size** | Maximum **10 MB** per request | `MAX_FILE_SIZE_MB` setting |
| **Concurrency** | Use `async`/`await` for I/O-bound endpoints | `async def upload_endpoint(...)` |

### Rate Limiting Configuration

Rate limits are applied via `slowapi` decorators on each endpoint. The global rate limit is set via `RATE_LIMIT_PER_MINUTE` (0 = disabled). Per-endpoint limits override the global limit.

```python
from app.infrastructure.rate_limiter import limiter

@router.post("/upload")
@limiter.limit(lambda: f"{settings.UPLOAD_RATE_LIMIT}/minute")
async def upload(request: Request, ...):
    ...
```

---

## Secrets Management

- **Never** hardcode secrets (e.g., `SECRET_KEY`, `DATABASE_URL`).
- Use **environment variables** (`.env` + `pydantic-settings`).

### Secure Configuration Example

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 100
    TOKEN_RATE_LIMIT: int = 20
    UPLOAD_RATE_LIMIT: int = 30
    EXPORT_RATE_LIMIT: int = 100
    MAX_BATCH_SIZE: int = 1000
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

## Structured Logging

```python
# app/infrastructure/repositories/order_repository.py
import logging

logger = logging.getLogger(__name__)

# Usage:
logger.info("Upload batch of %d orders by user %s", len(orders), user_id)
logger.exception("create_batch failed for %d orders, rolling back", len(orders))
```