from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.account_settings_model import AccountSettings
from app.models.review_model import ReviewModel
from app.models.salary_model import SalaryModel
from app.models.user_model import UserModel
from app.schemas.account_settings_schema import AccountSettingsUpdate
from app.schemas.user_schema import UserUpdateSchema


class ProfileService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def update_profile(self, user: UserModel, user_data: UserUpdateSchema) -> UserModel:
        data = user_data.model_dump(exclude_unset=True)

        if "email" in data and data["email"] != user.email:
            existing_user = await self._get_user_by_email(data["email"])
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

        if "username" in data and data["username"] != user.username:
            existing_user = await self._get_user_by_username(data["username"])
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")

        for field, value in data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, user: UserModel, current_password: str, new_password: str) -> None:
        if not user.hashed_password or not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.hashed_password = hash_password(new_password)
        await self.db.commit()

    async def get_contributions(self, user_id: int) -> dict:
        reviews_result = await self.db.execute(
            select(ReviewModel)
            .where(ReviewModel.user_id == user_id)
            .order_by(ReviewModel.created_at.desc())
        )
        salaries_result = await self.db.execute(
            select(SalaryModel)
            .where(SalaryModel.user_id == user_id)
            .order_by(SalaryModel.created_at.desc())
        )
        return {
            "reviews": reviews_result.scalars().all(),
            "salaries": salaries_result.scalars().all()
        }

    async def get_or_create_settings(self, user_id: int) -> AccountSettings:
        settings = await self._get_settings(user_id)
        if settings:
            return settings

        settings = AccountSettings(user_id=user_id)
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update_settings(self, user_id: int, settings_data: AccountSettingsUpdate) -> AccountSettings:
        settings = await self.get_or_create_settings(user_id)
        for field, value in settings_data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)

        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def _get_user_by_email(self, email: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()

    async def _get_user_by_username(self, username: str) -> UserModel | None:
        result = await self.db.execute(select(UserModel).where(UserModel.username == username))
        return result.scalar_one_or_none()

    async def _get_settings(self, user_id: int) -> AccountSettings | None:
        result = await self.db.execute(
            select(AccountSettings).where(AccountSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
