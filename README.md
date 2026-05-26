# API de Importación/Exportación Masiva con Validación Estricta

> API REST construida con FastAPI para importación/exportación masiva de datos relacionales con validación estricta de Pydantic, procesamiento parcial, autenticación JWT y reporte de errores RFC 7807.

## Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/Fisherk2/api-csv-bulk-import.git
cd api-csv-bulk-import

# Copiar variables de entorno
cp .env.example .env

# Iniciar el stack completo
docker-compose up

# Ejecutar pruebas
pytest --cov=app
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115+ |
| Validation | Pydantic 2.x |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Auth | JWT (OAuth2 Password Flow) |
| Testing | pytest + pytest-cov + pytest-mock |

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/token` | Obtener token JWT (OAuth2 Password Flow) |
| `POST` | `/upload` | Importar datos en formato CSV o JSON |
| `GET` | `/export` | Exportar datos en formato CSV o JSON |

## Documentación

- [SPEC.md](SPEC.md) — Especificación completa del proyecto
- [WORKFLOW.md](WORKFLOW.md) — Seguimiento de implementación y progreso por fases
- [AGENTS.md](AGENTS.md) — Referencia rápida y límites
- [Architecture & Design](docs/ARCHITECTURE.md) — Patrones, diagramas, estructura de carpetas
- [Domain & Requirements](docs/DOMAIN.md) — Entidades, requisitos, límites del sistema
- [Code Style & Conventions](docs/CODE-STYLE.md) — Nomenclatura, SOLID, reglas de archivos
- [Testing Strategy](docs/TESTING.md) — Fases de prueba, frameworks, fixtures, ejemplos
- [Security & Error Handling](docs/SECURITY.md) — Validación, respuestas HTTP, rate limiting

## Estado

🟡 **En Especificación** — El proyecto está en fase de especificación. Aún no hay implementación.

## License

MIT