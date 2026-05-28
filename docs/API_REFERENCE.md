# API Reference

Complete reference for all endpoints with `curl` examples.

**Base URL:** `http://localhost:8000`

**Authentication:** JWT Bearer token via OAuth2 Password Flow.

**Error Format:** All errors follow [RFC 7807 Problem Details](https://www.rfc-editor.org/rfc/rfc7807).

---

## Table of Contents

- [Health Check](#health-check)
- [Authentication](#authentication)
- [Upload Orders](#upload-orders)
- [Export Orders](#export-orders)
- [Error Responses](#error-responses)
- [Rate Limiting](#rate-limiting)

---

## Health Check

### `GET /`

Returns API status and version. No authentication required.

**Response:** `200 OK`

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**curl example:**

```bash
curl http://localhost:8000/
```

---

## Authentication

### `POST /token`

Obtain a JWT access token. Uses OAuth2 Password Flow with form-encoded body.

**Rate limit:** 20 requests per minute per IP.

**Request body:** `application/x-www-form-urlencoded`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | User's username (email) |
| `password` | string | Yes | User's password |

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**

| Status | Description |
|--------|-------------|
| `401` | Incorrect username or password |
| `401` | Inactive user |
| `422` | Missing required fields |
| `429` | Rate limit exceeded (RFC 7807) |

**curl example:**

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin@example.com&password=secret123"
```

---

## Upload Orders

### `POST /upload`

Import orders in JSON or CSV format. Requires JWT authentication.

**Rate limit:** 30 requests per minute per IP.

**Max batch size:** 1000 orders.
**Max file size:** 10 MB.

---

#### JSON Upload

**Request:** `application/json`

```json
{
  "orders": [
    {
      "customer_id": "550e8400-e29b-41d4-a716-446655440000",
      "items": [
        {
          "product_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
          "quantity": 2,
          "price": 29.99
        }
      ]
    }
  ]
}
```

**Field constraints:**

| Field | Type | Constraints |
|-------|------|-------------|
| `orders` | array | min: 1, max: 1000 |
| `customer_id` | UUID | Must reference existing customer |
| `items` | array | min: 1 item per order |
| `product_id` | UUID | Must reference existing product |
| `quantity` | integer | 1–1000 |
| `price` | float | 0 < price ≤ 1,000,000 |

**Response:** `200 OK` (all valid)

```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

**Response:** `207 Multi-Status` (partial success)

```json
{
  "total": 5,
  "successful": 3,
  "failed": 2,
  "errors": [
    {
      "type": "about:blank",
      "title": "Validation Error",
      "status": 422,
      "detail": "customer_id: Field required",
      "instance": null,
      "row_number": 2
    },
    {
      "type": "about:blank",
      "title": "Validation Error",
      "status": 422,
      "detail": "items: Field required",
      "instance": null,
      "row_number": 5
    }
  ]
}
```

**Response:** `422 Unprocessable Entity` (all invalid)

```json
{
  "total": 2,
  "successful": 0,
  "failed": 2,
  "errors": [
    {
      "type": "about:blank",
      "title": "Validation Error",
      "status": 422,
      "detail": "customer_id: Field required",
      "instance": null,
      "row_number": 1
    },
    {
      "type": "about:blank",
      "title": "Validation Error",
      "status": 422,
      "detail": "customer_id: Field required",
      "instance": null,
      "row_number": 2
    }
  ]
}
```

**curl example (JSON):**

```bash
TOKEN="<your-jwt-token>"

curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [
      {
        "customer_id": "550e8400-e29b-41d4-a716-446655440000",
        "items": [
          {
            "product_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "quantity": 2,
            "price": 29.99
          }
        ]
      }
    ]
  }'
```

---

#### CSV Upload

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | CSV file (UTF-8) |

**CSV format:** The CSV must include columns `customer_email`, `customer_name`, `product_id`, `quantity`, `price`, and `status`. Rows are grouped by `customer_email` into orders.

**Example CSV:**

```csv
customer_email,customer_name,product_id,quantity,price,status
alice@example.com,Alice Johnson,6ba7b810-9dad-11d1-80b4-00c04fd430c8,2,29.99,pending
alice@example.com,Alice Johnson,6ba7b810-9dad-11d1-80b4-00c04fd430c8,1,14.99,shipped
bob@example.com,Bob Smith,6ba7b810-9dad-11d1-80b4-00c04fd430c8,3,45.00,pending
```

**Response:** Same as JSON upload (200/207/422).

**curl example (CSV):**

```bash
TOKEN="<your-jwt-token>"

curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@orders.csv"
```

**Errors:**

| Status | Description |
|--------|-------------|
| `400` | Invalid CSV format or missing required columns |
| `401` | Missing or invalid JWT token |
| `413` | File exceeds 10 MB or batch exceeds 1000 rows |
| `422` | At least one order is required |
| `429` | Rate limit exceeded |

---

## Export Orders

### `GET /export`

Export orders in JSON or CSV format. Requires JWT authentication.

**Query parameters:**

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `format` | string | `json` | `json` or `csv` | Output format |
| `skip` | integer | `0` | ≥ 0 | Pagination offset |
| `limit` | integer | `100` | 1–1000 | Max records to return |

---

#### JSON Export

**Response:** `200 OK` — `application/json`

```json
[
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "items": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "product_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "quantity": 2,
        "price": 29.99
      }
    ],
    "created_at": "2026-05-27T10:30:00"
  }
]
```

**curl example:**

```bash
TOKEN="<your-jwt-token>"

curl http://localhost:8000/export \
  -H "Authorization: Bearer $TOKEN"
```

---

#### CSV Export

**Response:** `200 OK` — `text/csv`

```csv
order_id,customer_id,product_id,quantity,price,status,created_at
7c9e6679-7425-40de-944b-e07fc1f90ae7,550e8400-e29b-41d4-a716-446655440000,6ba7b810-9dad-11d1-80b4-00c04fd430c8,2,29.99,pending,2026-05-27 10:30:00
```

**curl example:**

```bash
TOKEN="<your-jwt-token>"

curl "http://localhost:8000/export?format=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o orders.csv
```

---

#### Pagination

```bash
TOKEN="<your-jwt-token>"

# Get first 50 records
curl "http://localhost:8000/export?skip=0&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Get next page
curl "http://localhost:8000/export?skip=50&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

**Errors:**

| Status | Description |
|--------|-------------|
| `400` | Invalid format parameter |
| `401` | Missing or invalid JWT token |
| `422` | Invalid query parameters |

---

## Error Responses

All errors follow [RFC 7807 Problem Details](https://www.rfc-editor.org/rfc/rfc7807):

```json
{
  "type": "about:blank",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Not authenticated",
  "instance": "/upload"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | URI reference identifying the error type |
| `title` | string | Short human-readable error summary |
| `status` | integer | HTTP status code |
| `detail` | string | Human-readable explanation specific to this occurrence |
| `instance` | string | URI reference identifying the specific occurrence |

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /token` | 20 req | per minute per IP |
| `POST /upload` | 30 req | per minute per IP |
| `GET /export` | 100 req | per minute per IP |

When rate limited, the API returns `429 Too Many Requests` in RFC 7807 format:

```json
{
  "type": "about:blank",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded: 100 per minute",
  "instance": null
}
```

---

## Quick Reference

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| `GET` | `/` | No | — | Health check |
| `POST` | `/token` | No | 20/min | Obtain JWT token |
| `POST` | `/upload` | Yes | 30/min | Import orders (JSON/CSV) |
| `GET` | `/export` | Yes | 100/min | Export orders (JSON/CSV) |

---

## Swagger UI

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

ReDoc alternative:

```
http://localhost:8000/redoc
```
