from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
