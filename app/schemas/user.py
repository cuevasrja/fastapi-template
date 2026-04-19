from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]
