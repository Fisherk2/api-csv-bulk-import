# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-27

### Añadido

- **API REST completa con FastAPI** — 4 endpoints operativos:
  - `GET /` — Health check con estado y versión
  - `POST /token` — Autenticación JWT (OAuth2 Password Flow)
  - `POST /upload` — Importación masiva de órdenes (CSV y JSON)
  - `GET /export` — Exportación de órdenes (CSV y JSON) con paginación (`skip`/`limit`)
- **Autenticación JWT** — Tokens con claims (`aud`, `iss`, `jti`), expiración configurable (30 min por defecto), verificación de audience
- **Procesamiento parcial** — Las filas válidas se insertan y las inválidas se reportan con errores detallados (HTTP 200/207/422/413)
- **Validación estricta con Pydantic** — Schemas con constraints (longitud, rango, email), sanitización (trim de whitespace), validación de tipos en parser CSV
- **Errores RFC 7807 (Problem Details)** — Formato estandarizado para todos los errores de validación, autenticación y rate limiting
- **Capa de dominio pura (`app/core/`)** — Entidades, repositorios (interfaces) y servicios con cero dependencias externas (solo stdlib)
- **Arquitectura DDD** — 5 entidades (User, Product, Customer, Order, OrderItem), 3 repositorios, 2 servicios de dominio, Repository + Service Layer patterns
- **Persistencia asíncrona** — SQLAlchemy 2.x async con asyncpg, sesiones asíncronas, Unit of Work
- **Migraciones Alembic** — 4 migraciones (users, products, customers, orders+items)
- **CSV/JSON parsers** — Parseo de CSV a órdenes agrupadas por email, soporte multipart y JSON body, detección de dialecto, validación de columnas requeridas
- **ExportService** — Exportación en JSON y CSV plano (1 fila por ítem), con paginación y sin dependencias del framework
- **Rate limiting** — `slowapi` con límites por endpoint: global 100 req/min, /token 20 req/min, /upload 30 req/min, /export 100 req/min, cabeceras rate limit, errores RFC 7807 429
- **Makefile** — 18 targets para flujo de trabajo (`make help`, `make lint`, `make test`, `make docker-up`, etc.)
- **Docker multi-stage** — Imagen < 300 MB con `python:3.12-slim`, usuario no-root, health checks, entrypoint con migraciones automáticas
- **Docker Compose** — `docker-compose.yml` (desarrollo) + `docker-compose.prod.yml` (producción con Nginx)
- **Nginx reverse proxy** — Seguridad (HSTS, CSP, Referrer-Policy, Permissions-Policy), `client_max_body_size 10m`, proxy_pass a la API
- **CI/CD (GitHub Actions)** — Pipeline con PostgreSQL 16 service container, lint + type-check + tests paralelos, gate de cobertura ≥ 80%
- **Tests completos** — 279 tests (unitarios, integración, E2E), cobertura 97.24%, 2 smoke tests Docker
- **Documentación técnica** — ARCHITECTURE.md, DOMAIN.md, CODE-STYLE.md, TESTING.md, SECURITY.md, API_REFERENCE.md, CONTRIBUTING.md, RETROSPECTIVE.md
- **Fichero de skills** — `skills-lock.json`, skills de FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Python testing
- **Exclusiones de directorios agénticos** — `pyproject.toml` excluye `agents/`, `.opencode/`, `skills/`, `commands/` de ruff y mypy

### Cambiado

- **Metodología** — De fases horizontales (F0-F6) a vertical slices (P1-P8): cada fase entrega funcionalidad completa end-to-end
- **Base de datos** — SQLAlchemy síncrono → asíncrono con asyncpg (runtime) + psycopg2-binary (Alembic)
- **Rate limiting** — Global genérico → límites por endpoint con `slowapi` y patrón singleton
- **Test fixtures** — De síncronas a asíncronas con `AsyncSession`, `httpx.AsyncClient`, `aiosqlite` para pruebas en memoria
- **Documentación** — AGENTS.md reestructurada con divulgación progresiva; CHANGELOG.md actualizado con información real del proyecto
- **Workflow de desarrollo** — Comandos raw reemplazados por targets de Makefile en toda la documentación
- **Formato de código** — Ruff format aplicado consistentemente a todos los archivos del proyecto

### Corregido

- **P1:** 4 hallazgos de code review (tipos, imports, estructura) + 2 opcionales (simplificación, typing)
- **P4:** Observaciones de code review en servicio, repositorios y esquemas
- **P5:** Hallazgos de code review + simplificación de tipo de retorno en `export_orders_raw`
- **P6:** Correcciones en las 5 dimensiones (correctitud, legibilidad, arquitectura, seguridad, rendimiento)
- **P7:** Proxy de health check en Nginx, variable DB_PASSWORD parametrizada, errores 429 en formato RFC 7807
- **P8:** Tests Docker smoke, advertencias de deprecación de FastAPI
- **`datetime.utcnow()`** reemplazado por `datetime.now(timezone.utc)` (deprecado en Python 3.12)
- **`create_batch`** en los 3 repositorios: ahora re-lanza la excepción después de `rollback()` para evitar pérdida silenciosa de datos (AD-P3-04 actualizado)
- **Documentación:** Contradicciones resueltas en 11 archivos (cobertura, estados de fase, módulos eliminados, reglas de contraseña, rate limits, ejemplos obsoletos)
- **Ficheros vacíos** eliminados: `docs/SETUP.md`, `scripts/build.sh`, `scripts/lint.sh`, `scripts/setup.sh`, `scripts/test.sh`, `.gitmessage`

### Seguridad

- **Claims JWT** — `aud`, `iss`, `jti` añadidos a los tokens para validación de alcance
- **Complejidad de contraseñas** — Mínimo: mayúscula, minúscula, dígito (8+ caracteres)
- **Rate limiting por endpoint** — Límites específicos para upload (30/min), export (100/min) y token (20/min)
- **Cabeceras de seguridad en Nginx** — HSTS, Content-Security-Policy, Referrer-Policy, Permissions-Policy, X-Content-Type-Options
- **Validación de Content-Type** — Rechazo de MIME types incorrectos en uploads multipart (CSV)
- **Validación de tipos en parser CSV** — `int()`/`float()` envueltos en try/except con contexto de fila y número de línea
- **Contenedor no-root** — La imagen Docker ejecuta la API como `appuser` no privilegiado
- **TLS/HTTPS** — Plantilla de configuración SSL incluida en Nginx para producción
- **Variables de entorno** — Todos los secretos (DB_PASSWORD, SECRET_KEY) parametrizados, nunca hardcodeados

### Eliminado

- **ValidationService** — Código muerto que nunca era llamado desde el flujo de upload
- **`ICustomerRepository`** — Dependencia no utilizada en `OrderService`
- **Directorio `.windsurf/`** — Archivos de configuración de Windsurf obsoletos
- **Ficheros vacíos** — `docs/SETUP.md`, scripts `build.sh`, `lint.sh`, `setup.sh`, `test.sh`, `.gitmessage`
- **Reglas de `.gitignore`** — Reglas no utilizadas y duplicadas limpiadas

---

## Información del Proyecto

### Repositorio
- **Nombre**: API de Importación/Exportación Masiva con Validación Estricta
- **Descripción**: REST API en FastAPI para importación/exportación masiva de datos relacionales (órdenes, productos, clientes) con validación estricta de Pydantic, procesamiento parcial (filas válidas se insertan, inválidas se reportan), autenticación JWT y errores RFC 7807
- **Repositorio**: https://github.com/Fisherk2/api-csv-bulk-import/
- **Licencia**: MIT License

### Stack Tecnológico
- **Lenguaje**: Python 3.12+
- **Framework**: FastAPI 0.115+
- **Validación**: Pydantic 2.x
- **ORM**: SQLAlchemy 2.x
- **Migraciones**: Alembic 1.13+
- **Base de Datos**: PostgreSQL 16
- **Autenticación**: python-jose + passlib (JWT, OAuth2 Password Flow)
- **Testing**: pytest + pytest-cov + pytest-mock
- **Linting**: ruff
- **Type Checking**: mypy (strict mode)
- **Contenedores**: Docker + Docker Compose

### Arquitectura
- **Patrón**: Domain-Driven Design (DDD) con Repository, Service Layer, Unit of Work
- **Estilo de Errores**: RFC 7807 (Problem Details)
- **Metodología**: Spec-Driven Development (SDD) con Vertical Slices

### Documentación
- **[README.md](README.md)** — Guía rápida del proyecto
- **[SPEC.md](SPEC.md)** — Especificación de requisitos y criterios de éxito
- **[AGENTS.md](AGENTS.md)** — Referencia técnica, stack, convenciones de código
- **[WORKFLOW.md](WORKFLOW.md)** — Roadmap de implementación y seguimiento de fases
- **[tasks/plan.md](tasks/plan.md)** — Plan detallado con tareas verticales (T01–T28)
- **[tasks/todo.md](tasks/todo.md)** — Checklist de progreso por fase
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Patrones de arquitectura, diagramas, estructura de carpetas
- **[docs/DOMAIN.md](docs/DOMAIN.md)** — Entidades, requisitos funcionales/no funcionales, límites del sistema
- **[docs/CODE-STYLE.md](docs/CODE-STYLE.md)** — Convenciones de nomenclatura, SOLID, reglas de archivos
- **[docs/TESTING.md](docs/TESTING.md)** — Estrategia de pruebas, pirámide de testing, cobertura objetivo
- **[docs/SECURITY.md](docs/SECURITY.md)** — Validación de entrada, rate limiting, secretos, logging

### Estado Actual
| Fase | Estado | Fecha |
|------|--------|-------|
| P1: Foundation | ✅ Completed | 2026-05-25 |
| P2: Auth Slice | ✅ Completed | 2026-05-28 |
| P3: Product Slice | ✅ Completed | 2026-05-26 |
| P4: Upload Slice | ✅ Completed | 2026-05-26 |
| P5: Export Slice | ✅ Completed | 2026-05-26 |
| P6: Testing | ✅ Completed | 2026-05-27 |
| P7: Deployment | ✅ Completed | 2026-05-27 |
| P8: Closure | ✅ Completed | 2026-06-06 |
