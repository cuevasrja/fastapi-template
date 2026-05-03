from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password to receive a JWT access token.",
)
async def login(
    payload: LoginRequest,
    conn: Annotated[AsyncConnection, Depends(get_db)],
) -> TokenResponse:
    try:
        return await auth_service.login(conn, payload)
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)
