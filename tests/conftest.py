import psycopg
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi_test"

_CREATE_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name   VARCHAR(100) NOT NULL,
    role        VARCHAR(50)  NOT NULL DEFAULT 'user',
    is_active   BOOLEAN      NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
"""

_DROP_SCHEMA = "DROP TABLE IF EXISTS users;"


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    conn = await psycopg.AsyncConnection.connect(TEST_DATABASE_URL, autocommit=True)
    await conn.execute(_CREATE_SCHEMA)
    await conn.close()
    yield
    conn = await psycopg.AsyncConnection.connect(TEST_DATABASE_URL, autocommit=True)
    await conn.execute(_DROP_SCHEMA)
    await conn.close()


@pytest.fixture
async def db_session():
    conn = await psycopg.AsyncConnection.connect(TEST_DATABASE_URL)
    try:
        yield conn
        await conn.rollback()
    finally:
        await conn.close()


@pytest.fixture
async def client(db_session: psycopg.AsyncConnection):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
