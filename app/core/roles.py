from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.models.user_model import UserRole

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

def require_role(required_role: UserRole):
    async def role_checker(
        token: str,
        auth_service: AuthService = Depends(get_auth_service)
    ):
        user = await auth_service.get_current_user(token)
        if user.role != required_role.value:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_role.value}"
            )
        return user
    return role_checker

# Удобные алиасы
require_admin = require_role(UserRole.ADMIN)
require_moderator = require_role(UserRole.MODERATOR)
require_user = require_role(UserRole.USER)