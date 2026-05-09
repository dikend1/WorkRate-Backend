from fastapi import Depends, HTTPException
from app.core.dependencies import get_current_user
from app.models.user_model import UserModel
from app.models.user_model import UserRole


def require_role(required_role: UserRole):
    async def role_checker(
        user: UserModel = Depends(get_current_user)
    ):
        if user.role != required_role.value:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_role.value}"
            )
        return user
    return role_checker

def require_any_role(*required_roles: UserRole):
    async def role_checker(
        user: UserModel = Depends(get_current_user)
    ):
        allowed_roles = {role.value for role in required_roles}
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required one of: {', '.join(sorted(allowed_roles))}"
            )
        return user
    return role_checker

# Удобные алиасы
require_admin = require_role(UserRole.ADMIN)
require_admin_or_moderator = require_any_role(UserRole.ADMIN, UserRole.MODERATOR)
