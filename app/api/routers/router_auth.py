from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserBaseSchema, UserCreateSchema, UserResponseSchema, TokenSchema
from app.models.user_model import UserModel, UserRole
from app.core.security import decode_access_token
from app.core.config import settings
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.roles import require_admin, require_moderator
import secrets
from app.core.roles import  require_admin, require_moderator


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)



# Настройка OAuth2 клиента для Google
oauth_client = AsyncOAuth2Client(
    client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
    client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/google/callback"
)




@router.post("/register", response_model=UserResponseSchema)
async def register_user(
    data: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register_user(
        email=data.email,
        password=data.password,
        username=data.username,
        role="user"  # Обычные пользователи регистрируются с ролью user
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

# Admin routes
@router.post("/admin/users", response_model=UserResponseSchema)
async def create_user_by_admin(
    email: str,
    password: str,
    username: str,
    role: str = "user",
    user = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Создание пользователя админом с указанием роли"""
    new_user = await auth_service.register_user(
        email=email,
        password=password,
        username=username,
        role=role
    )
    return new_user

@router.get("/admin/dashboard")
async def admin_dashboard(user = Depends(require_admin)):
    return {
        "message": "Admin dashboard",
        "user": user.email,
        "role": user.role
    }

@router.get("/moderator/reviews")
async def moderator_reviews(user = Depends(require_moderator)):
    return {
        "message": "Pending reviews for moderation",
        "moderator": user.email,
        "role": user.role
    }

# Google OAuth routes with Authlib
@router.get("/google/login")
async def google_login():
    # Создаем authorization URL с Authlib
    authorization_url, state = oauth_client.create_authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        scope=['openid', 'email', 'profile']
    )
    
    return {"auth_url": authorization_url, "state": state}

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        # Используем Authlib для обмена кода на токен
        token = await oauth_client.fetch_token(
            'https://oauth2.googleapis.com/token',
            authorization_response=f'http://localhost:8000/auth/google/callback?code={code}&state={state}'
        )

        if not token or 'access_token' not in token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        access_token = token['access_token']

        # Получаем информацию о пользователе
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with AsyncOAuth2Client() as client:
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

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

    
    