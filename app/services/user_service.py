from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.core.exceptions import ConflictException, ForbiddenException, ResourceNotFoundException
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.common import _is_admin

_UPDATABLE_FIELDS = frozenset({"full_name", "is_active"})


async def get_all(conn: AsyncConnection, current_user: User) -> list[User]:
    if not await _is_admin(current_user):
        raise ForbiddenException()
    async with conn.cursor(row_factory=class_row(User)) as cur:
        await cur.execute("SELECT * FROM users ORDER BY created_at DESC")
        return await cur.fetchall()


async def get_by_id(conn: AsyncConnection, user_id: UUID, current_user: User) -> User:
    if not await _is_admin(current_user) and current_user.id != user_id:
        raise ForbiddenException()
    async with conn.cursor(row_factory=class_row(User)) as cur:
        await cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = await cur.fetchone()
    if not user:
        raise ResourceNotFoundException("User", str(user_id))
    return user


async def create(conn: AsyncConnection, payload: UserCreate) -> User:
    async with conn.cursor(row_factory=class_row(User)) as cur:
        await cur.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
        if await cur.fetchone():
            raise ConflictException(f"User with email '{payload.email}' already exists")
        await cur.execute(
            """
            INSERT INTO users (email, hashed_password, full_name)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (payload.email, hash_password(payload.password.get_secret_value()), payload.full_name),
        )
        return await cur.fetchone()


async def update(
    conn: AsyncConnection, user_id: UUID, payload: UserUpdate, current_user: User
) -> User:
    if not await _is_admin(current_user) and current_user.id != user_id:
        raise ForbiddenException()

    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items() if k in _UPDATABLE_FIELDS}
    if not updates:
        return await get_by_id(conn, user_id, current_user)

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = [*updates.values(), user_id]

    async with conn.cursor(row_factory=class_row(User)) as cur:
        await cur.execute(
            f"UPDATE users SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *",
            values,
        )
        user = await cur.fetchone()
    if not user:
        raise ResourceNotFoundException("User", str(user_id))
    return user


async def delete(conn: AsyncConnection, user_id: UUID, current_user: User) -> None:
    if not await _is_admin(current_user):
        raise ForbiddenException()
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
        if not await cur.fetchone():
            raise ResourceNotFoundException("User", str(user_id))
