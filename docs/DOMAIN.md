# Domain & Requirements

**Project:** API de Importación/Exportación Masiva con Validación Estricta

---

## Domain Entities

| Entity | Fields | Description |
|--------|--------|-------------|
| `Order` | `id`, `customer_id`, `created_at`, `status` | Customer order |
| `OrderItem` | `order_id`, `product_id`, `quantity`, `price` | Item within an order |
| `Product` | `id`, `name`, `price`, `stock` | Available product |
| `Customer` | `id`, `name`, `email` | Registered customer |
| `User` | `id`, `username`, `hashed_password` | Authentication user |

---

## Functional Requirements

| ID | Description | Priority |
|----|-------------|----------|
| RF-001 | `POST /upload` endpoint for CSV/JSON data import | High |
| RF-002 | `GET /export` endpoint for CSV/JSON data export | High |
| RF-003 | Strict Pydantic schema validation (required fields, ranges, uniqueness) | High |
| RF-004 | Partial processing: insert valid data only, report errors | High |
| RF-005 | JWT authentication for sensitive endpoints (`/upload`, `/export`) | High |
| RF-006 | RFC 7807 (Problem Details) error reports | High |

## Non-Functional Requirements

| ID | Description | Priority |
|----|-------------|----------|
| RNF-001 | Standardized HTTP responses (200, 207, 400, 401, 403, 422) | High |
| RNF-002 | Structured JSON logging for debugging | Medium |
| RNF-003 | Linear processing time relative to batch size O(n) | High |
| RNF-004 | PostgreSQL with optimized indexes for frequent queries | Medium |
| RNF-005 | Automatic OpenAPI (Swagger) documentation | Medium |

---

## System Boundaries

### In Scope (MVP)
- `/upload` (POST) and `/export` (GET) endpoints
- Strict Pydantic validation
- PostgreSQL persistence
- JWT authentication
- RFC 7807 error reports
- Partial data processing
- OpenAPI documentation
- Unit, integration, and E2E tests

### Out of Scope
- Payment gateway integrations
- Email/SMS notifications
- File storage (in-memory processing only)
- Horizontal scaling (local MVP focus)
- Advanced monitoring (e.g., Prometheus)

### External Integrations
- None in MVP (focus on internal logic)

---

## Implementation Order

1. **Infrastructure:** PostgreSQL setup, FastAPI config, JWT authentication
2. **Domain:** Data models (SQLAlchemy + Pydantic) and repositories
3. **Business Logic:** Import/export use cases and validation
4. **API:** `/upload` and `/export` endpoints
5. **Testing:** Unit, integration, and E2E
6. **Documentation:** OpenAPI, README, usage examples