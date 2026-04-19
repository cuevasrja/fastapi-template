# FastAPI Template

Plantilla de backend con **FastAPI**, arquitectura en capas (Router → Service → Model), PostgreSQL, JWT auth y documentación OpenAPI automática.

---

## Estructura del proyecto

```plaintext
fastapi-template/
├── app/
│   ├── core/           # Config, DB, seguridad, excepciones
│   ├── models/         # Modelos SQLAlchemy 2.0 (async, UUID PKs)
│   ├── schemas/        # Schemas Pydantic v2 (request/response)
│   ├── services/       # Lógica de negocio y RBAC
│   ├── routers/        # Endpoints HTTP (Router layer)
│   ├── dependencies.py # Inyección de dependencias (auth)
│   └── main.py         # Aplicación FastAPI
├── migrations/         # Alembic migrations
├── tests/              # Suite de pruebas
├── docker-compose.yml  # PostgreSQL local
├── justfile            # Comandos del proyecto
├── requirements.txt
└── .env.example
```

---

## Requisitos previos

- Python 3.12+
- [just](https://github.com/casey/just) — task runner (`cargo install just` o `brew install just`)
- Docker + Docker Compose

---

## Inicio rapido

### 1. Clonar y configurar entorno

```bash
git clone <repo-url>
cd fastapi-template

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

just install
just env-setup              # Crea .env desde .env.example
```

Editar `.env` y cambiar `SECRET_KEY` por un valor seguro:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Levantar la base de datos

```bash
just db-up
```

Esto inicia PostgreSQL en `localhost:5432` con las credenciales del `.env`.

### 3. Aplicar migraciones

```bash
just migrate
```

### 4. Iniciar el servidor

```bash
just run
```

El servidor estara disponible en `http://localhost:8000`.

---

## Documentacion OpenAPI

FastAPI genera la documentacion automaticamente:

| URL | Descripcion |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI (interactivo) |
| `http://localhost:8000/redoc` | ReDoc (legible) |
| `http://localhost:8000/openapi.json` | Schema JSON crudo |

---

## Endpoints disponibles

### Health

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/health` | Health check |

### Autenticacion

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `POST` | `/auth/login` | Login — devuelve JWT |

### Usuarios

| Metodo | Ruta | Auth | Descripcion |
|--------|------|------|-------------|
| `POST` | `/users/` | No | Registrar nuevo usuario |
| `GET` | `/users/me` | Si | Perfil del usuario actual |
| `GET` | `/users/` | Admin | Listar todos los usuarios |
| `GET` | `/users/{id}` | Si | Obtener usuario por ID |
| `PATCH` | `/users/{id}` | Si | Actualizar usuario |
| `DELETE` | `/users/{id}` | Admin | Eliminar usuario |

---

## Flujo de autenticacion

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword123", "full_name": "Juan Perez"}'

# 2. Hacer login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword123"}'

# 3. Usar el token
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <token>"
```

---

## Migraciones (Alembic)

```bash
# Crear migracion despues de modificar un modelo
just migrate-create "descripcion del cambio"

# Aplicar migraciones pendientes
just migrate

# Revertir ultima migracion
just migrate-rollback

# Ver estado actual
just migrate-status
```

---

## Tests

```bash
# Requiere la base de datos levantada (just db-up)
just test

# Con reporte de cobertura
just test-cov
```

Los tests usan una base de datos separada `fastapi_test`. Crear la BD antes de correr los tests:

```bash
docker exec -it fastapi_postgres psql -U postgres -c "CREATE DATABASE fastapi_test;"
```

---

## Linting y formato

```bash
just lint     # Revisar errores con ruff
just format   # Formatear codigo
just check    # Verificar sin modificar (para CI)
```

---

## Agregar un nuevo recurso

Sigue este patron para cada nuevo modulo:

1. **Model** — `app/models/item.py` (SQLAlchemy, UUID PK)
2. **Schema** — `app/schemas/item.py` (Pydantic v2, `from_attributes=True`)
3. **Service** — `app/services/item_service.py` (logica de negocio + RBAC)
4. **Router** — `app/routers/item.py` (HTTP handlers, `Annotated` DI)
5. **Registrar** — añadir `app.include_router(item.router)` en `app/main.py`
6. **Migrar** — `just migrate-create "add items table"` + `just migrate`

---

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `APP_NAME` | `FastAPI Template` | Nombre de la app |
| `DEBUG` | `false` | Habilita logs SQL |
| `DATABASE_URL` | `postgresql+asyncpg://...` | URL de conexion async |
| `SECRET_KEY` | — | Clave para firmar JWT (cambiar!) |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Duracion del token |

---

## Comandos `just` disponibles

```bash
just install          Instalar dependencias
just run              Servidor de desarrollo
just serve            Servidor de produccion (4 workers)
just db-up            Levantar PostgreSQL con Docker
just db-down          Detener PostgreSQL
just db-reset         Resetear BD (destructivo)
just migrate          Aplicar migraciones
just migrate-create   Crear nueva migracion
just migrate-rollback Revertir ultima migracion
just test             Correr tests
just test-cov         Tests con cobertura
just lint             Revisar con ruff
just format           Formatear codigo
just env-setup        Crear .env desde .env.example
```
