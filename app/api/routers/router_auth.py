from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserBaseSchema, UserCreateSchema, UserResponseSchema, TokenSchema
from app.models.user_model import UserModel
from app.core.security import decode_access_token
from app.core.config import settings
from starlette.requests import Request
from starlette.responses import RedirectResponse
import httpx
import secrets


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


@router.post("/register", response_model=UserResponseSchema)
async def register_user(
    data: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register_user(
        email=data.email,
        password=data.password,
        username=data.username
    )
    return user

@router.post("/login", response_model=TokenSchema)
async def login_user(
    email: str,
    password: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.login_user(
        email=email,
        password=password
    )
    token = await auth_service.create_token(user)
    return token

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
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
    
    # Получаем пользователя
    user = await auth_service.get_current_user(token)
    token_data = await auth_service.create_token(user)
    return token_data

@router.get("/me", response_model=UserResponseSchema)
async def get_me(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_current_user(token)
    return user

# Альтернативный вариант с токеном в теле запроса
@router.post("/me", response_model=UserResponseSchema)
async def get_me_post(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_current_user(token)
    return user

# Google OAuth routes
@router.get("/google/login")
async def google_login():
    # Генерируем state для защиты от CSRF
    state = secrets.token_urlsafe(32)
    
    # URL для авторизации Google
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.OAUTH_GOOGLE_CLIENT_ID}&"
        "response_type=code&"
        "scope=openid email profile&"
        f"redirect_uri=http://localhost:8000/auth/google/callback&"
        f"state={state}"
    )
    
    return {"auth_url": google_auth_url, "state": state}

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    # Обмениваем код на токен
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8000/auth/google/callback"
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if "access_token" not in token_json:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        access_token = token_json["access_token"]
        
        # Получаем информацию о пользователе
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = await client.get(user_info_url, headers=headers)
        user_info = user_response.json()
        
        email = user_info.get("email")
        google_id = user_info.get("id")
        name = user_info.get("name", "")
        
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Ищем пользователя по google_id или email
        from sqlalchemy import select
        query = select(UserModel).where(
            (UserModel.google_id == google_id) | (UserModel.email == email)
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем нового пользователя
            username = email.split("@")[0]  # Простой username из email
            user = UserModel(
                email=email,
                username=username,
                google_id=google_id,
                is_verified=True  # Google аккаунты считаем верифицированными
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Создаем токен
        token_data = await auth_service.create_token(user)
        return token_data