from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


async def login(conn: AsyncConnection, payload: LoginRequest) -> TokenResponse:
    async with conn.cursor(row_factory=class_row(User)) as cur:
        await cur.execute("SELECT * FROM users WHERE email = %s", (payload.email,))
        user = await cur.fetchone()

    if not user or not verify_password(payload.password.get_secret_value(), user.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException("Account is disabled")

    token = create_access_token(subject=str(user.id), extra={"role": user.role})
    return TokenResponse(access_token=token)
