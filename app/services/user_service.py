from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, ResourceNotFoundException
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.common import _is_admin


async def get_all(db: AsyncSession, current_user: User) -> list[User]:
    if not await _is_admin(current_user):
        raise ForbiddenException()
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, user_id: UUID, current_user: User) -> User:
    if not await _is_admin(current_user) and current_user.id != user_id:
        raise ForbiddenException()
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ResourceNotFoundException("User", str(user_id))
    return user


async def create(db: AsyncSession, payload: UserCreate) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise ConflictException(f"User with email '{payload.email}' already exists")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password.get_secret_value()),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update(
    db: AsyncSession, user_id: UUID, payload: UserUpdate, current_user: User
) -> User:
    user = await get_by_id(db, user_id, current_user)

    if not await _is_admin(current_user) and current_user.id != user_id:
        raise ForbiddenException()

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user_id: UUID, current_user: User) -> None:
    if not await _is_admin(current_user):
        raise ForbiddenException()
    user = await get_by_id(db, user_id, current_user)
    await db.delete(user)
