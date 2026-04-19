from app.models.user import User


async def _is_admin(current_user: User) -> bool:
    return current_user.role == "admin"
