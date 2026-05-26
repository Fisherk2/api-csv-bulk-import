# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Sin Lanzar]

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
| P2: Auth Slice | 🟡 Ready for Specs | — |
| P3: Product Slice | ❌ Not started | — |
| P4: Upload Slice | ❌ Not started | — |
| P5: Export Slice | ❌ Not started | — |
| P6: Testing | ❌ Not started | — |
| P7: Deployment | ❌ Not started | — |
| P8: Closure | ❌ Not started | — |
