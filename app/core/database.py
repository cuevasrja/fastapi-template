from collections.abc import AsyncGenerator

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings

_pool: AsyncConnectionPool | None = None


async def init_pool() -> None:
    global _pool
    _pool = AsyncConnectionPool(conninfo=settings.DATABASE_URL, open=False)
    await _pool.open()


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    async with _pool.connection() as conn:
        yield conn
