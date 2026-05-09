from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import UserModel
from fastapi import HTTPException, status
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_purpose_token,
    decode_access_token
)
from app.core.redis_client import redis_client


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    

    async def register_user(
        self,
        email: str,
        password: str = None,
        username: str = None,
        google_id: str = None,
        facebook_id: str = None,
        role: str = "user",
        first_name: str = None,
        last_name: str = None,
        profile_picture: str = None,
        current_position: str = None,
        current_company_id: int = None
    ):
        query = select(UserModel).where(UserModel.email == email)
        existing_user = (await self.db.execute(query)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if not username or username == "string":
            username = await self._generate_unique_username(email)

        if not google_id and not facebook_id:
            # Для обычной регистрации проверяем username
            query = select(UserModel).where(UserModel.username == username)
            existing_user = (await self.db.execute(query)).scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        hashed_password = hash_password(password) if password else None
        
        user = UserModel(
            email=email,
            username=username,
            hashed_password=hashed_password,
            google_id=google_id,
            facebook_id=facebook_id,
            is_verified=bool(google_id or facebook_id),  # OAuth пользователи автоматически верифицированы
            role=role,
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture,
            current_position=current_position,
            current_company_id=current_company_id
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def _generate_unique_username(self, email: str) -> str:
        base_username = email.split("@")[0].strip().lower() or "user"
        candidate = base_username
        suffix = 1

        while True:
            query = select(UserModel).where(UserModel.username == candidate)
            existing_user = (await self.db.execute(query)).scalar_one_or_none()
            if not existing_user:
                return candidate

            suffix += 1
            candidate = f"{base_username}{suffix}"
    
    async def login_user(self,email:str,password:str):
        query = select(UserModel).where(UserModel.email == email)
        user = (await self.db.execute(query)).scalar_one_or_none()
        if not user or not verify_password(password,user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return user
    
    async def create_token(self,user:UserModel):
        payload = {"sub": str(user.id),"email": user.email}
        access_token = create_access_token(payload)
        refresh_token = create_access_token(payload)  
        
        # Сохраняем refresh токен в Redis (опционально)
        try:
            await redis_client.set(f"refresh_token:{user.id}", refresh_token)
        except Exception:
            # Redis не доступен, пропускаем
            pass
            
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def create_email_confirmation_token(self, user: UserModel) -> str:
        return create_purpose_token(
            {"sub": str(user.id), "email": user.email},
            "email_confirmation",
            expires_minutes=60 * 24
        )

    async def confirm_email(self, token: str) -> UserModel:
        user = await self._get_user_from_purpose_token(token, "email_confirmation")
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_password_reset_token(self, email: str) -> str:
        query = select(UserModel).where(UserModel.email == email)
        user = (await self.db.execute(query)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return create_purpose_token(
            {"sub": str(user.id), "email": user.email},
            "password_reset",
            expires_minutes=60
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self._get_user_from_purpose_token(token, "password_reset")
        user.hashed_password = hash_password(new_password)
        await self.db.commit()
    
    async def get_current_user(self, token: str):
        payload = decode_access_token(token)
        if payload == "JWT None":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        query = select(UserModel).where(UserModel.id == int(user_id))
        user = (await self.db.execute(query)).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user

    async def _get_user_from_purpose_token(self, token: str, purpose: str) -> UserModel:
        payload = decode_access_token(token)
        if payload == "JWT None" or payload.get("purpose") != purpose:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        query = select(UserModel).where(UserModel.id == int(user_id))
        user = (await self.db.execute(query)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
