# FastAPI Template

Plantilla de backend con **FastAPI**, arquitectura en capas (Router → Service → Model), PostgreSQL + **pgvector**, JWT auth y documentación OpenAPI automática.

El acceso a la base de datos usa **psycopg3** con SQL directo — sin ORM. Las migraciones se escriben como SQL puro y se ejecutan con Alembic.

---

## Estructura del proyecto

```plaintext
fastapi-template/
├── app/
│   ├── core/           # Config, pool de conexiones, seguridad, excepciones
│   ├── models/         # Dataclasses Python (mapeo de filas psycopg3)
│   ├── schemas/        # Schemas Pydantic v2 (request/response)
│   ├── services/       # Lógica de negocio — SQL directo con psycopg3
│   ├── routers/        # Endpoints HTTP (Router layer)
│   ├── dependencies.py # Inyección de dependencias (auth)
│   └── main.py         # Aplicación FastAPI + lifespan (pool init/close)
├── migrations/
│   └── versions/       # Migraciones SQL escritas a mano
├── scripts/
│   └── init-pgvector.sql  # Habilita la extensión vector al crear el contenedor
├── tests/              # Suite de pruebas
├── docker-compose.yml  # PostgreSQL + pgvector local
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

## Inicio rápido

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

Inicia PostgreSQL 17 con la extensión **pgvector** pre-instalada en `localhost:5432`.

### 3. Aplicar migraciones

```bash
just migrate
```

### 4. Iniciar el servidor

```bash
just run
```

El servidor estará disponible en `http://localhost:8000`.

---

## Documentación OpenAPI

| URL | Descripción |
| --- | --- |
| `http://localhost:8000/docs` | Swagger UI (interactivo) |
| `http://localhost:8000/redoc` | ReDoc (legible) |
| `http://localhost:8000/openapi.json` | Schema JSON crudo |

---

## Endpoints disponibles

### Health

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Health check |

### Autenticación

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/auth/login` | Login — devuelve JWT |

### Usuarios

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `POST` | `/users/` | No | Registrar nuevo usuario |
| `GET` | `/users/me` | Sí | Perfil del usuario actual |
| `GET` | `/users/` | Admin | Listar todos los usuarios |
| `GET` | `/users/{id}` | Sí | Obtener usuario por ID |
| `PATCH` | `/users/{id}` | Sí | Actualizar usuario |
| `DELETE` | `/users/{id}` | Admin | Eliminar usuario |

---

## Flujo de autenticación

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

## Migraciones

Las migraciones son **SQL puro** ejecutado por Alembic. No hay autogeneración desde modelos ORM — cada cambio en el esquema se escribe a mano en el archivo de migración correspondiente.

### Comandos

```bash
just migrate-create "descripcion"   # Genera archivo vacío en migrations/versions/
just migrate                        # Aplica todas las migraciones pendientes
just migrate-rollback               # Revierte la última migración (corre downgrade)
just migrate-status                 # Muestra la revisión actualmente aplicada
just migrate-history                # Lista todas las revisiones con detalle
```

### Estructura de un archivo de migración

```python
# migrations/versions/0002_add_products_table.py

from alembic import op

revision = "0002"
down_revision = "0001"   # revisión anterior — forma el grafo de orden
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE products (
            id         UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
            name       VARCHAR(255)  NOT NULL,
            price      NUMERIC(10,2) NOT NULL,
            user_id    UUID          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW()
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS products;")
```

### Ejemplos de operaciones comunes

**Agregar columna:**

```python
def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20);")

def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN phone;")
```

**Renombrar columna:**

```python
def upgrade() -> None:
    op.execute("ALTER TABLE users RENAME COLUMN full_name TO display_name;")

def downgrade() -> None:
    op.execute("ALTER TABLE users RENAME COLUMN display_name TO full_name;")
```

**Agregar índice:**

```python
def upgrade() -> None:
    op.execute("CREATE INDEX ix_users_role ON users (role);")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_role;")
```

**Columna vectorial con pgvector:**

```python
def upgrade() -> None:
    op.execute("""
        ALTER TABLE products ADD COLUMN embedding vector(1536);
        CREATE INDEX ON products
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """)

def downgrade() -> None:
    op.execute("ALTER TABLE products DROP COLUMN embedding;")
```

### Reglas

- Siempre escribir `downgrade()` con el inverso exacto del `upgrade()`.
- Nombrar archivos con prefijo numérico (`0002_`, `0003_`) para que el orden sea legible.
- Nunca modificar una migración ya aplicada — crear una nueva que corrija.
- El campo `down_revision` forma el grafo; debe apuntar a la revisión inmediatamente anterior.

---

## Cómo agregar un nuevo recurso

1. **Migración** — `just migrate-create "add items table"`, escribir el `CREATE TABLE` en el archivo generado y correr `just migrate`
2. **Model** — `app/models/item.py` (dataclass Python con los mismos campos que la tabla)
3. **Schema** — `app/schemas/item.py` (Pydantic v2, `model_config = ConfigDict(from_attributes=True)`)
4. **Service** — `app/services/item_service.py` (SQL directo con `conn.cursor(row_factory=class_row(Item))`)
5. **Router** — `app/routers/item.py` (handlers HTTP, inyectar `AsyncConnection` con `Depends(get_db)`)
6. **Registrar** — añadir `app.include_router(item.router)` en `app/main.py`

### Patrón de servicio con psycopg3

```python
from psycopg import AsyncConnection
from psycopg.rows import class_row
from app.models.item import Item

async def get_by_id(conn: AsyncConnection, item_id: UUID) -> Item:
    async with conn.cursor(row_factory=class_row(Item)) as cur:
        await cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = await cur.fetchone()
    if not item:
        raise ResourceNotFoundException("Item", str(item_id))
    return item

async def create(conn: AsyncConnection, payload: ItemCreate) -> Item:
    async with conn.cursor(row_factory=class_row(Item)) as cur:
        await cur.execute(
            "INSERT INTO items (name, price) VALUES (%s, %s) RETURNING *",
            (payload.name, payload.price),
        )
        return await cur.fetchone()
```

> `class_row(Item)` mapea automáticamente los nombres de columna del resultado a los campos del dataclass. Siempre usar `RETURNING *` en INSERT/UPDATE para obtener el registro con los valores generados por la DB (id, timestamps).

---

## pgvector

La imagen Docker `pgvector/pgvector:pg17` incluye la extensión preinstalada. Se habilita automáticamente al crear el contenedor via `scripts/init-pgvector.sql`.

Para usar vectores en una tabla nueva, agregar la columna en la migración:

```sql
ALTER TABLE items ADD COLUMN embedding vector(1536);
```

Y consultar por similitud coseno:

```python
await cur.execute(
    "SELECT * FROM items ORDER BY embedding <=> %s LIMIT 10",
    (query_vector,),
)
```

---

## Tests

```bash
# Requiere la base de datos levantada (just db-up)
just test

# Con reporte de cobertura
just test-cov
```

Los tests usan una base de datos separada `fastapi_test`. Crearla antes de correr los tests por primera vez:

```bash
docker exec -it fastapi_postgres psql -U postgres -c "CREATE DATABASE fastapi_test;"
```

Cada test corre dentro de una transacción que se revierte al finalizar — la base de datos queda limpia entre pruebas sin necesidad de truncar tablas.

---

## Docker

```bash
just db-up            # Levantar PostgreSQL
just db-down          # Detener contenedores
just rebuild          # Bajar, actualizar imágenes y volver a levantar (preserva volúmenes)
just db-reset         # Resetear BD eliminando volúmenes (destructivo)
just db-extensions    # Listar extensiones instaladas (nombre, versión, schema)
```

---

## Linting y formato

```bash
just lint     # Revisar errores con ruff
just format   # Formatear código
just check    # Verificar sin modificar (para CI)
```

---

## Variables de entorno

| Variable | Default | Descripción |
| ---------- | --------- | ------------- |
| `APP_NAME` | `FastAPI Template` | Nombre de la app |
| `DEBUG` | `false` | Habilita logs verbose |
| `DATABASE_URL` | `postgresql://...` | URL de conexión psycopg3 |
| `SECRET_KEY` | — | Clave para firmar JWT (cambiar en producción) |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Duración del token |

---

## Comandos `just` disponibles

```bash
just install            # Instalar dependencias
just run                # Servidor de desarrollo (hot reload)
just serve              # Servidor de producción (4 workers)
just db-up              # Levantar PostgreSQL con Docker
just db-down            # Detener contenedores
just rebuild            # Actualizar imágenes y recrear contenedores
just db-reset           # Resetear BD (destructivo, elimina volúmenes)
just db-extensions      # Listar extensiones instaladas en PostgreSQL
just migrate            # Aplicar migraciones pendientes
just migrate-create     # Crear nueva migración
just migrate-rollback   # Revertir última migración
just migrate-status     # Ver revisión actual
just migrate-history    # Ver historial de migraciones
just test               # Correr tests
just test-cov           # Tests con cobertura
just lint               # Revisar con ruff
just format             # Formatear código
just check              # Verificar formato sin modificar (CI)
just env-setup          # Crear .env desde .env.example
```
