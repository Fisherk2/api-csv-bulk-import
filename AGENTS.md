# **📜 AGENTS.MD**
**Proyecto:** API de Importación/Exportación Masiva con Validación Estricta
**Versión:** 1.0.0
**Fecha:** 2026-05-25
**Autor:** Fisherk2
**Estado:** En Especificación
**Metodología:** Spec-Driven Development (SDD)
**Repositorio:** https://github.com/Fisherk2/api-csv-bulk-import/

---

## **🎯 Contexto del Proyecto**

### **Descripción MVP**
API REST desarrollada con **FastAPI** que permite:
- **Importar** datos masivos en formato **CSV/JSON** (detección automática).
- **Validar** los datos contra esquemas **Pydantic** con reglas estrictas (ej: `product_id > 0`, `customer_id` existe en DB).
- **Persistir** los datos válidos en **PostgreSQL** con manejo de transacciones por lote.
- **Exportar** datos en formato CSV/JSON.
- **Autenticación** mediante **JWT** (OAuth2 Password Flow).
- **Reportes de errores** estandarizados según **RFC 7807** para procesamiento parcial.

**Propósito:** Herramienta para **portafolio técnico**, demostrando:
✅ Validación estricta con Pydantic.
✅ Manejo de datos relacionales (pedidos, productos, clientes).
✅ Procesamiento parcial con transacciones controladas.
✅ Autenticación JWT y seguridad.
✅ Arquitectura **Domain-Driven Design (DDD)**.

---

### **Requisitos Funcionales y No Funcionales**

| **Tipo**            | **ID**   | **Descripción**                                                                                     | **Prioridad** | **Cumple** |
|---------------------|----------|-----------------------------------------------------------------------------------------------------|---------------|------------|
| **Funcional**       | RF-001   | Endpoint `POST /upload` para importar datos en CSV/JSON.                                            | Alta          | ✅          |
| **Funcional**       | RF-002   | Endpoint `GET /export` para exportar datos en CSV/JSON.                                             | Alta          | ✅          |
| **Funcional**       | RF-003   | Validación estricta de esquemas con Pydantic (ej: campos obligatorios, rangos, unicidad).          | Alta          | ✅          |
| **Funcional**       | RF-004   | Procesamiento parcial: insertar solo datos válidos y reportar errores.                            | Alta          | ✅          |
| **Funcional**       | RF-005   | Autenticación JWT para endpoints sensibles (`/upload`, `/export`).                                | Alta          | ✅          |
| **Funcional**       | RF-006   | Reportes de errores en formato **RFC 7807** (Problem Details).                                     | Alta          | ✅          |
| **No Funcional**    | RNF-001  | Respuestas HTTP estandarizadas (200, 207, 400, 401, 403, 422).                                    | Alta          | ✅          |
| **No Funcional**    | RNF-002  | Logs estructurados (JSON) para debugging.                                                          | Media         | ✅          |
| **No Funcional**    | RNF-003  | Tiempo de procesamiento lineal respecto al tamaño del lote (O(n)).                               | Alta          | ✅          |
| **No Funcional**    | RNF-004  | Base de datos PostgreSQL con índices optimizados para búsquedas frecuentes.                       | Media         | ✅          |
| **No Funcional**    | RNF-005  | Documentación OpenAPI (Swagger) automática.                                                        | Media         | ✅          |

---

### **Dominio y Límites del Sistema**
**Dominio:**
- **Entidades principales:**
  - `Order` (pedido): `id`, `customer_id`, `created_at`, `status`.
  - `OrderItem` (ítem de pedido): `order_id`, `product_id`, `quantity`, `price`.
  - `Product` (producto): `id`, `name`, `price`, `stock`.
  - `Customer` (cliente): `id`, `name`, `email`.
  - `User` (usuario para autenticación): `id`, `username`, `hashed_password`.

**Límites:**
- La API **no** manejará:
  - Pagos o integración con pasarelas de pago.
  - Notificaciones por email/SMS.
  - Almacenamiento de archivos (solo procesamiento en memoria).
- **Integraciones externas:** Ninguna en el MVP (foco en lógica interna).

**Orden de Implementación Propuesto:**
1. **Infraestructura:** Configuración de PostgreSQL, FastAPI, y autenticación JWT.
2. **Dominio:** Modelos de datos (SQLAlchemy + Pydantic) y repositorios.
3. **Lógica de Negocio:** Casos de uso para importación/exportación y validación.
4. **API:** Endpoints `/upload` y `/export`.
5. **Pruebas:** Unitarias, integración, y E2E.
6. **Documentación:** OpenAPI, README, y ejemplos de uso.

---

## **🏗️ Arquitectura y Diseño**

### **Patrones Arquitectónicos Aplicados**
| **Patrón**               | **Aplicación en el Proyecto**                                                                                     | **Beneficio**                                                                 |
|--------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **Domain-Driven Design** | Organización por dominios (`orders/`, `products/`, `customers/`).                                              | Separación clara de responsabilidades y alta cohesión.                     |
| **Contract-First**       | Esquemas Pydantic definidos **antes** que los endpoints.                                                        | Validación consistente y documentación automática (OpenAPI).                 |
| **Fail-Fast**            | Validación de datos **antes** de procesar el lote.                                                              | Evita estados inconsistentes en la DB.                                        |
| **Repository Pattern**   | Capa de abstracción para acceso a datos (ej: `OrderRepository`).                                               | Desacopla la lógica de negocio de la persistencia.                          |
| **Dependency Injection** | Inyección de dependencias (ej: repositorios, servicios de autenticación) en los casos de uso.                  | Facilita testing y mocking.                                                   |
| **Unit of Work**         | Manejo de transacciones por lote (validación previa + `INSERT ... ON CONFLICT`).                                | Consistencia y procesamiento parcial.                                       |

---

### **Diagrama de Componentes y Flujo de Datos**
```mermaid
graph TD
    %% --- Actores ---
    A[Cliente] -->|1. POST /upload| B[FastAPI]
    A -->|2. GET /export| B
    A -->|3. POST /token| B

    %% --- Capa de API ---
    B -->|Autenticación JWT| C[Auth Middleware]
    C -->|Valida Token| D[Endpoints]
    D -->|/upload| E[Upload Use Case]
    D -->|/export| F[Export Use Case]
    D -->|/token| G[Auth Use Case]

    %% --- Capa de Aplicación ---
    E -->|2. Valida datos| H[Validation Service]
    H -->|Usa esquemas| I[Pydantic Schemas]
    E -->|3. Procesa lote| J[Order Service]
    J -->|4. Persiste datos| K[Order Repository]
    F -->|Consulta datos| K

    %% --- Capa de Infraestructura ---
    K -->|SQLAlchemy| L[(PostgreSQL)]
    G -->|JWT| M[JWT Service]
    M -->|Secrets| N[.env]

    %% --- Respuestas ---
    E -->|5. Reporte RFC 7807| D
    D -->|6. Respuesta HTTP| A
    F -->|7. Datos exportados| A

    %% --- Estilos ---
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
    style D fill:#bbf,stroke:#333
    style E fill:#9f9,stroke:#333
    style F fill:#9f9,stroke:#333
    style G fill:#9f9,stroke:#333
    style H fill:#9f9,stroke:#333
    style J fill:#9f9,stroke:#333
    style K fill:#ff9,stroke:#333
    style L fill:#ff9,stroke:#333
    style M fill:#ff9,stroke:#333
    style N fill:#ff9,stroke:#333
```

**Flujo detallado para `/upload`:**
1. **Autenticación:** El cliente envía un token JWT en el header `Authorization: Bearer <token>`.
2. **Parsing:** FastAPI detecta el formato (CSV/JSON) y lo convierte a un objeto Python.
3. **Validación:** `ValidationService` valida cada fila/objeto contra los esquemas Pydantic.
4. **Procesamiento:**
   - Si hay errores, se generan en formato RFC 7807.
   - Si no hay errores, `OrderService` prepara el lote para persistencia.
5. **Persistencia:** `OrderRepository` inserta los datos válidos en PostgreSQL con `INSERT ... ON CONFLICT DO NOTHING`.
6. **Respuesta:** FastAPI devuelve:
   - **200 OK** si todo el lote es válido.
   - **207 Multi-Status** si hay errores parciales (con reporte RFC 7807).
   - **422 Unprocessable Entity** si todas las filas son inválidas.

---
### **Estructura de Carpetas (DDD)**
```
api-import-export/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Configuración de FastAPI y rutas principales
│   ├── config.py                # Variables de entorno y configuración
│   ├── dependencies.py          # Inyección de dependencias (ej: get_db, get_current_user)
│   │
│   ├── core/                    # Dominio (lógica de negocio pura)
│   │   ├── __init__.py
│   │   ├── entities/            # Entidades de dominio (sin SQLAlchemy)
│   │   │   ├── order.py
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   └── user.py
│   │   ├── repositories/        # Interfaces de repositorio (contratos)
│   │   │   ├── order_repository.py
│   │   │   ├── product_repository.py
│   │   │   └── customer_repository.py
│   │   └── services/            # Servicios de dominio (lógica de negocio)
│   │       ├── validation_service.py
│   │       └── order_service.py
│   │
│   ├── infrastructure/          # Detalles de implementación
│   │   ├── __init__.py
│   │   ├── database/            # Configuración de DB y modelos SQLAlchemy
│   │   │   ├── base.py          # Base declarativa de SQLAlchemy
│   │   │   ├── models/          # Modelos SQLAlchemy
│   │   │   │   ├── order.py
│   │   │   │   ├── product.py
│   │   │   │   ├── customer.py
│   │   │   │   └── user.py
│   │   │   └── session.py       # Configuración de sesiones y conexión
│   │   ├── repositories/        # Implementaciones de repositorios
│   │   │   ├── order_repository.py
│   │   │   ├── product_repository.py
│   │   │   └── customer_repository.py
│   │   ├── auth/                # Autenticación
│   │   │   ├── jwt_service.py   # Lógica de JWT
│   │   │   ├── password_service.py # Hashing de contraseñas
│   │   │   └── dependencies.py  # Dependencias de autenticación (ej: get_current_user)
│   │   └── api/                 # Endpoints y rutas
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── upload.py
│   │       │   ├── export.py
│   │       │   └── auth.py
│   │       └── routers.py        # Routers de FastAPI
│   │
│   ├── schemas/                 # Esquemas Pydantic (request/response)
│   │   ├── __init__.py
│   │   ├── order.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── user.py
│   │   └── error.py             # Esquemas para errores (RFC 7807)
│   │
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── csv_parser.py        # Parsing de CSV a dicts
│       ├── json_parser.py       # Parsing de JSON
│       └── file_utils.py        # Detección de formato (CSV/JSON)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures para pytest
│   ├── unit/
│   │   ├── test_validation.py
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   ├── integration/
│   │   ├── test_upload.py
│   │   └── test_export.py
│   └── e2e/
│       └── test_api.py
│
├── migrations/                 # Migraciones de Alembic
│   └── versions/
│
├── .env.example                 # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt
├── pyproject.toml               # Configuración de proyecto (poetry)
└── README.md
```

---
### **Justificación Técnica de Elecciones Críticas**
| **Decisión**                          | **Alternativas Consideradas**               | **Justificación**                                                                                     |
|---------------------------------------|---------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **DDD sobre Clean Architecture**      | Clean Architecture, Layered Simple         | DDD permite organizar el código por **dominio**, lo que es más intuitivo para datos relacionales.   |
| **JWT para autenticación**             | API Key, OAuth2                             | JWT es **estándar**, fácil de implementar con FastAPI, y demuestra conocimiento de seguridad.       |
| **Procesamiento parcial (207)**        | Todo o nada (422), Errores agregados        | Permite al cliente **corregir solo las filas problemáticas**, mejorando la experiencia de usuario.   |
| **RFC 7807 para errores**               | Formato simple, Formato detallado custom    | **Estandarizado**, interoperable, y demuestra buenas prácticas en diseño de APIs.                     |
| **Transacciones por lote**             | Transacción única, Transacciones por fila   | Equilibrio entre **consistencia** y **procesamiento parcial**.                                       |
| **Pydantic para validación**           | Marshmallow, manual                         | **Integración nativa con FastAPI**, tipado estático, y validación declarativa.                       |
| **PostgreSQL**                         | SQLite, MySQL                              | **Soporte nativo para JSON**, transacciones avanzadas, y escalabilidad.                              |

---

## **🔧 Guías de Desarrollo**

### **Principios SOLID Aplicados**
| **Principio**       | **Aplicación en el Proyecto**                                                                                     | **Ejemplo**                                                                                     |
|---------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| **Single Responsibility** | Cada clase/módulo tiene una única responsabilidad.                                                             | `OrderRepository` solo maneja operaciones de DB para `Order`.                                  |
| **Open/Closed**      | Las entidades y servicios están abiertos a extensión pero cerrados a modificación.                            | `ValidationService` puede extenderse para añadir nuevas reglas sin modificar el código existente. |
| **Liskov Substitution** | Las implementaciones de repositorios pueden sustituirse por sus interfaces sin afectar el comportamiento.      | `OrderRepository` (SQLAlchemy) implementa `IOrderRepository`.                                  |
| **Interface Segregation** | Las interfaces de repositorio son específicas para cada entidad.                                               | `IOrderRepository` solo tiene métodos relacionados con `Order`.                                |
| **Dependency Inversion** | Los casos de uso dependen de abstracciones (interfaces), no de implementaciones concretas.                     | `UploadUseCase` depende de `IOrderRepository`, no de `OrderRepository`.                        |

---
### **Patrones de Diseño**
| **Patrón**               | **Aplicación**                                                                                     | **Beneficio**                                                                                     |
|--------------------------|---------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| **Repository**           | `OrderRepository`, `ProductRepository` (abstracción de acceso a datos).                          | Desacopla la lógica de negocio de la persistencia.                                              |
| **Service Layer**        | `OrderService`, `ValidationService` (lógica de negocio).                                         | Centraliza la lógica de negocio y facilita su reutilización.                                    |
| **Dependency Injection** | Inyección de repositorios y servicios en casos de uso.                                           | Facilita testing (mocking) y flexibilidad.                                                       |
| **Unit of Work**         | Manejo de transacciones por lote en `OrderService`.                                               | Garantiza consistencia en operaciones complejas.                                                |
| **Factory**              | `PydanticSchemaFactory` (para crear esquemas dinámicos si se extiende el MVP).                   | Permite flexibilidad en la creación de objetos.                                                  |
| **Adapter**              | `CSVParser`, `JSONParser` (normalización de entrada).                                            | Permite manejar múltiples formatos de entrada con una interfaz común.                         |

---
### **Convenciones de Nomenclatura**
| **Tipo**               | **Convención**                          | **Ejemplo**                          |
|------------------------|-----------------------------------------|--------------------------------------|
| **Clases (Pydantic)**  | PascalCase, sufijo `Schema`              | `OrderCreateSchema`                  |
| **Clases (SQLAlchemy)**| PascalCase, sufijo `Model`               | `OrderModel`                         |
| **Entidades (DDD)**    | PascalCase                              | `Order`, `Product`                   |
| **Repositorios**       | PascalCase, sufijo `Repository`          | `OrderRepository`                    |
| **Servicios**          | PascalCase, sufijo `Service`             | `OrderService`                       |
| **Casos de Uso**       | PascalCase, sufijo `UseCase`             | `UploadOrderUseCase`                 |
| **Endpoints**          | snake_case                              | `upload_order`, `export_orders`      |
| **Variables**          | snake_case                              | `order_id`, `customer_name`          |
| **Funciones**          | snake_case                              | `validate_order`, `parse_csv`        |
| **Archivos**           | snake_case                              | `order_repository.py`, `upload.py`   |
| **Constantes**         | UPPER_SNAKE_CASE                        | `MAX_BATCH_SIZE = 1000`              |

---
### **Estructura de Carpetas y Archivos**
- **Regla 1:** Cada archivo debe tener **máximo 300 líneas** (excepción: `__init__.py` para exports).
- **Regla 2:** Los archivos de prueba deben reflejar la estructura del código fuente (ej: `tests/unit/test_order_service.py`).
- **Regla 3:** Usar **`__init__.py`** para exponer símbolos públicos (ej: en `app/core/entities/__init__.py`:
  ```python
  from .order import Order
  from .product import Product
  __all__ = ["Order", "Product"]
  ```
  
---
### **Checklists de Pre-Commit**
**Todos los commits deben pasar las siguientes verificaciones:**
- [ ] **Linter:** `ruff check .` (sin errores).
- [ ] **Formateador:** `ruff format .` (código formateado).
- [ ] **Tipado:** `mypy .` (sin errores de tipo).
- [ ] **Pruebas:** `pytest` (todas las pruebas pasan).
- [ ] **Migraciones:** `alembic revision --autogenerate` (si hay cambios en modelos).
- [ ] **Documentación:** Actualizar `README.md` y docstrings si es necesario.

**Herramientas recomendadas:**
```toml
# pyproject.toml (ejemplo con poetry)
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
### **Estrategia de Manejo de Errores y Fallbacks**
| **Tipo de Error**               | **Manejo**                                                                                     | **Código HTTP** | **Formato de Respuesta**               |
|---------------------------------|------------------------------------------------------------------------------------------------|-----------------|----------------------------------------|
| **Validación (Pydantic)**       | Capturar `ValidationError` y convertir a RFC 7807.                                            | 422             | RFC 7807 (Problem Details)             |
| **Autenticación (JWT inválido)**| `HTTPException(401, detail="Invalid token")`.                                                  | 401             | RFC 7807                                 |
| **Autorización (sin permisos)** | `HTTPException(403, detail="Not authorized")`.                                                 | 403             | RFC 7807                                 |
| **Base de datos (conflicto)**   | `IntegrityError` → `HTTPException(409, detail="Conflict")`.                                    | 409             | RFC 7807                                 |
| **Base de datos (error genérico)** | Loggear error y devolver `HTTPException(500, detail="Internal server error")`.               | 500             | RFC 7807                                 |
| **Formato inválido (CSV/JSON)** | `HTTPException(400, detail="Invalid format")`.                                                 | 400             | RFC 7807                                 |
| **Tamaño de lote excedido**     | `HTTPException(413, detail="Batch size exceeds limit")`.                                       | 413             | RFC 7807                                 |
**Fallbacks:**
- **Timeout en DB:** Reintentar la transacción **1 vez** antes de fallar.
- **Error en parsing CSV/JSON:** Devolver error con el **número de fila** y **campo problemático**.

---
## **🧪 Testing y Calidad**

### **Estrategia de Pruebas en 3 Fases**
| **Fase**          | **Tipo de Prueba**       | **Objetivo**                                                                                     | **Herramientas**               | **Cobertura Mínima** |
|-------------------|--------------------------|-------------------------------------------------------------------------------------------------|--------------------------------|----------------------|
| **Unitarias**     | Funciones y clases       | Validar lógica aislada (ej: validación, servicios).                                            | `pytest`, `pytest-mock`        | 90%                  |
| **Integración**   | Interacción entre módulos| Validar flujos completos (ej: `/upload` → validación → persistencia).                          | `pytest`, `TestClient`         | 80%                  |
| **E2E**           | Flujos de usuario        | Validar la API como un todo (ej: autenticación + `/upload` + `/export`).                        | `pytest`, `httpx`              | 70%                  |

---
### **Frameworks y Fixtures**
**Frameworks:**
- **Pruebas unitarias:** `pytest` + `pytest-mock`.
- **Pruebas de integración:** `TestClient` de FastAPI.
- **Pruebas E2E:** `httpx` (para requests HTTP reales).
- **Cobertura:** `pytest-cov`.

**Fixtures (ejemplo en `tests/conftest.py`):**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_db

# Fixture para la base de datos de prueba
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

# Fixture para el cliente de FastAPI
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
### **Ejemplos de Pruebas**
**1. Prueba unitaria para validación (Pydantic):**
```python
# tests/unit/test_validation.py
from pydantic import ValidationError
import pytest
from app.schemas.order import OrderCreateSchema

def test_order_validation_positive_price():
    with pytest.raises(ValidationError) as exc_info:
        OrderCreateSchema(
            customer_id=1,
            items=[{"product_id": 1, "quantity": 2, "price": -10.0}]  # Precio negativo
        )
    assert "price" in str(exc_info.value)
    assert "must be greater than 0" in str(exc_info.value)
```

**2. Prueba de integración para `/upload`:**
```python
# tests/integration/test_upload.py
def test_upload_valid_order(client, test_db_session):
    # Datos válidos
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

**3. Prueba E2E para flujo completo:**
```python
# tests/e2e/test_api.py
def test_full_flow(client):
    # 1. Login para obtener token
    login_data = {"username": "testuser", "password": "testpass"}
    login_response = client.post("/token", data=login_data)
    token = login_response.json()["access_token"]

    # 2. Upload con token
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
### **Métricas de Calidad**
| **Métrica**               | **Herramienta**       | **Objetivo**               | **Límite Aceptable** |
|---------------------------|-----------------------|----------------------------|----------------------|
| Cobertura de código       | `pytest-cov`          | % de código cubierto por pruebas | ≥ 80%               |
| Complejidad ciclomática   | `radon`               | Complejidad por función   | ≤ 10                 |
| Deuda técnica             | `sonarcloud` (opcional)| Issues de código           | 0 críticos           |
| Duplicación de código     | `ruff`                | % de código duplicado      | ≤ 5%                 |

---
### **Estrategia de Mockeo y Aislamiento**
- **Repositorios:** Usar `pytest-mock` para mockear llamadas a la DB.
  ```python
  def test_upload_service(mocker):
      mock_repo = mocker.MagicMock()
      mock_repo.insert_order.return_value = Order(id=1)
      service = OrderService(repository=mock_repo)
      result = service.create_order(order_data)
      assert result.id == 1
      mock_repo.insert_order.assert_called_once()
  ```
- **Servicios externos:** Si en el futuro se integran APIs externas, usar `httpx.MockTransport`.
- **Autenticación:** Mockear `get_current_user` en pruebas de endpoints.
  ```python
  from fastapi import Depends
  from fastapi.security import OAuth2PasswordBearer

  @pytest.fixture
  def mock_current_user():
      return {"username": "testuser", "id": 1}

  def test_upload_endpoint(client, mock_current_user, mocker):
      mocker.patch("app.api.endpoints.upload.get_current_user", return_value=mock_current_user)
      response = client.post("/upload", json={"orders": []})
      assert response.status_code == 200
  ```

---
## **🔒 Seguridad y Prohibiciones**

### **Validación de Inputs y Sanitización**
| **Campo**               | **Validación**                                                                                     | **Sanitización**                          |
|-------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------|
| **IDs**                 | Entero positivo (`gt=0`).                                                                         | Ninguna (PostgreSQL maneja tipos).        |
| **Nombres**             | `str`, `min_length=1`, `max_length=100`, regex para evitar inyección SQL.                         | `strip()` para eliminar espacios.         |
| **Emails**              | `EmailStr` (Pydantic).                                                                             | Ninguna (Pydantic valida formato).        |
| **Contraseñas**         | `min_length=8`, `max_length=50`, al menos 1 mayúscula, 1 número, 1 símbolo.                       | Hashing con `bcrypt`.                     |
| **Precios**             | `float`, `gt=0`, `le=1000000`.                                                                     | Redondeo a 2 decimales.                   |
| **Cantidad (quantity)** | `int`, `gt=0`, `le=1000`.                                                                          | Ninguna.                                  |
| **CSV/JSON**            | Validar estructura (ej: headers requeridos en CSV, campos obligatorios en JSON).               | Parsing con librerías seguras (`csv`, `json`). |

**Ejemplo de sanitización en Pydantic:**
```python
from pydantic import BaseModel, field_validator

class ProductCreateSchema(BaseModel):
    name: str
    price: float

    @field_validator("name")
    def sanitize_name(cls, v: str) -> str:
        return v.strip()  # Elimina espacios al inicio/final
```

---
### **Control de Excepciones, Timeouts y Rate Limiting**
| **Escenario**               | **Manejo**                                                                                     | **Configuración**                          |
|-----------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------|
| **Timeout en DB**           | Reintentar 1 vez con `tenacity`.                                                               | `retry=Retrying(stop=stop_after_attempt(2))` |
| **Rate Limiting**           | Limitar a **100 requests/minuto** por IP.                                                     | `slowapi` (FastAPI middleware).            |
| **Tamaño de lote**          | Máximo **1000 filas** por request.                                                             | Validar en `UploadUseCase`.                |
| **Tamaño de archivo**       | Máximo **10 MB** por request.                                                                  | `max_file_size=10_000_000` en FastAPI.     |
| **Concurrencia**            | Usar `async`/`await` para endpoints I/O-bound (ej: `/upload`).                                  | `async def upload_endpoint(...)`.          |

**Ejemplo de rate limiting con `slowapi`:**
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
### **Manejo de Secretos**
- **Nunca** hardcodear secretos (ej: `SECRET_KEY`, `DATABASE_URL`).
- Usar **variables de entorno** (`.env` + `pydantic-settings`).
- **Ejemplo de configuración segura:**
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
- **`.env.example`** (para compartir en el repositorio):
  ```
  SECRET_KEY=your_secret_key_here
  DATABASE_URL=postgresql://user:password@localhost:5432/db_name
  ```

---
### **Lista de Prácticas Prohibidas**
| **Práctica**                          | **Razón**                                                                                     | **Alternativa**                          |
|---------------------------------------|-----------------------------------------------------------------------------------------------|------------------------------------------|
| Hardcodear secretos                   | Riesgo de seguridad.                                                                          | Variables de entorno.                    |
| Usar `print` para debugging           | No estructurado, difícil de filtrar.                                                          | `logging` con formato JSON.              |
| Ignorar excepciones                  | Puede dejar la aplicación en estado inconsistente.                                          | Manejar todas las excepciones explícitamente. |
| Transacciones largas                 | Bloquea la DB y reduce rendimiento.                                                          | Dividir en transacciones pequeñas.       |
| SQL crudo en el código                | Riesgo de inyección SQL.                                                                      | Usar SQLAlchemy ORM o Core.              |
| Validación en el endpoint             | Acopla lógica de negocio a la capa de API.                                                    | Validación en `ValidationService`.       |
| Retornar datos sensibles en errores   | Riesgo de exposición de información (ej: stack traces).                                       | Mensajes genéricos + logs internos.      |
| Usar `any` como tipo                  | Pierde tipado estático.                                                                       | Usar tipos específicos o `Typing.Any`.   |
| Modificar el estado global            | Dificulta testing y debugging.                                                                | Usar inyección de dependencias.          |
| Acoplamiento temporal                 | Dificulta reutilización y testing.                                                            | Usar patrones como **Repository** o **Service Layer**. |

---
### **Ejemplo de Logging Estructurado**
```python
# app/config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter JSON
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)d %(pathname)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

# Uso en el código:
logger.info("Processing batch", extra={"batch_size": 100, "user_id": 1})
logger.error("Validation failed", extra={"errors": ["row 3: invalid price"]})
```

---
## **📌 Anexos**
- **Documentación relacionada:**
  - [FastAPI Official Docs](https://fastapi.tiangolo.com/)
  - [Pydantic Docs](https://docs.pydantic.dev/latest/)
  - [SQLAlchemy Docs](https://www.sqlalchemy.org/docs/)
  - [RFC 7807 (Problem Details)](https://datatracker.ietf.org/doc/html/rfc7807)
  - [DDD Reference](https://domainlanguage.com/ddd/reference/)
- **Plantillas:**
  - `WORKFLOW.MD` (orden de implementación).
  - `CONTRIBUTING.MD` (guía para contribuir).
  - `Dockerfile` y `docker-compose.yml` (para despliegue local).

---
## **💡 Notas para la IA Agentica**
1. **Prioridad de implementación:**
   - Seguir el orden definido en `WORKFLOW.MD` (Fase 0 → Fase 6).
   - **No implementar** un *spec* si sus dependencias no están completas (ej: no implementar `/upload` sin `ValidationService`).

2. **Reglas de código:**
   - **Siempre** usar tipado estático (`: type`).
   - **Siempre** incluir docstrings en funciones/clases (formato Google).
   - **Nunca** usar `pass` en bloques de código (usar `...` o `raise NotImplementedError`).

3. **Testing:**
   - Cada *spec* debe incluir pruebas unitarias y de integración.
   - Usar `pytest` y cubrir al menos el 80% del código.

4. **Documentación:**
   - Actualizar `AGENTS.MD` y `WORKFLOW.MD` al completar cada *spec*.
   - Incluir ejemplos de uso en el `README.md`.

5. **Seguridad:**
   - Validar **todos** los inputs (incluso los de APIs internas).
   - Usar `HTTPS` en producción (configurar en `main.py` con `UVicorn`).

---
