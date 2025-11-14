from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import UserModel, UserRole
from fastapi import HTTPException, status
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.core.redis_client import redis_client 


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    

    async def register_user(self, email: str, password: str = None, username: str = None, google_id: str = None, role: str = "user"):
        query = select(UserModel).where(UserModel.email == email)
        existing_user = (await self.db.execute(query)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if not google_id:
            # Для обычной регистрации проверяем username
            query = select(UserModel).where(UserModel.username == username)
            existing_user = (await self.db.execute(query)).scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        hashed_password = hash_password(password) if password else None
        if not username and google_id:
            username = email.split("@")[0]  # Автоматический username для OAuth
        
        user = UserModel(
            email=email,
            username=username,
            hashed_password=hashed_password,
            google_id=google_id,
            is_verified=bool(google_id),  # OAuth пользователи автоматически верифицированы
            role=role
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
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
    
    async def verify_refresh_token(self,user_id:int, refresh_token:str):
        try:
            stored = await redis_client.get(f"refresh_token:{user_id}")
            if stored != refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            return True
        except Exception:
            # Redis не доступен, пропускаем проверку
            return True

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


    