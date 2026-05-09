from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user_model import UserModel
from app.schemas.account_settings_schema import AccountSettingsResponse, AccountSettingsUpdate
from app.schemas.user_schema import (
    PasswordChangeSchema,
    UserContributionsSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/profile", tags=["Profile"])


def get_profile_service(db: AsyncSession = Depends(get_db)):
    return ProfileService(db)


@router.get("/me", response_model=UserResponseSchema)
async def get_profile(
    user: UserModel = Depends(get_current_user)
):
    return user


@router.patch("/me", response_model=UserResponseSchema)
async def update_profile(
    user_data: UserUpdateSchema,
    user: UserModel = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.update_profile(user, user_data)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeSchema,
    user: UserModel = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    await profile_service.change_password(
        user,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password changed"}


@router.get("/contributions", response_model=UserContributionsSchema)
async def get_contributions(
    user: UserModel = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.get_contributions(user.id)


@router.get("/settings", response_model=AccountSettingsResponse)
async def get_account_settings(
    user: UserModel = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.get_or_create_settings(user.id)


@router.patch("/settings", response_model=AccountSettingsResponse)
async def update_account_settings(
    settings_data: AccountSettingsUpdate,
    user: UserModel = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.update_settings(user.id, settings_data)
