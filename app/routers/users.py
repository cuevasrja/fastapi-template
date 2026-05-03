from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection

from app.core.database import get_db
from app.core.exceptions import ConflictException, ForbiddenException, ResourceNotFoundException
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def create_user(
    payload: UserCreate,
    conn: Annotated[AsyncConnection, Depends(get_db)],
) -> UserResponse:
    try:
        return await user_service.create(conn, payload)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users (admin only)",
)
async def list_users(
    conn: Annotated[AsyncConnection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserListResponse:
    try:
        users = await user_service.get_all(conn, current_user)
        return UserListResponse(total=len(users), items=users)
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.detail)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
async def get_user(
    user_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    try:
        return await user_service.get_by_id(conn, user_id, current_user)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.detail)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    try:
        return await user_service.update(conn, user_id, payload, current_user)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.detail)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
)
async def delete_user(
    user_id: UUID,
    conn: Annotated[AsyncConnection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        await user_service.delete(conn, user_id, current_user)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.detail)
