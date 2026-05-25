# Security & Error Handling

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## Input Validation & Sanitization

| Field | Validation | Sanitization |
|-------|-----------|-------------|
| **IDs** | Positive integer (`gt=0`) | None (PostgreSQL handles types) |
| **Names** | `str`, `min_length=1`, `max_length=100`, regex to prevent SQL injection | `strip()` to remove whitespace |
| **Emails** | `EmailStr` (Pydantic) | None (Pydantic validates format) |
| **Passwords** | `min_length=8`, `max_length=50`, at least 1 uppercase, 1 number, 1 symbol | Hashing with `bcrypt` |
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
| **DB Timeout** | Retry 1 time with `tenacity` | `retry=Retrying(stop=stop_after_attempt(2))` |
| **Rate Limiting** | Limit to **100 requests/minute** per IP | `slowapi` (FastAPI middleware) |
| **Batch Size** | Maximum **1000 rows** per request | Validate in `UploadUseCase` |
| **File Size** | Maximum **10 MB** per request | `max_file_size=10_000_000` in FastAPI |
| **Concurrency** | Use `async`/`await` for I/O-bound endpoints | `async def upload_endpoint(...)` |

### Rate Limiting Example

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/upload")
@limiter.limit("100/minute")
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
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### `.env.example` (for repository sharing)

```
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
```

---

## Structured Logging

```python
# app/config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)d %(pathname)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

# Usage:
logger.info("Processing batch", extra={"batch_size": 100, "user_id": 1})
logger.error("Validation failed", extra={"errors": ["row 3: invalid price"]})
```