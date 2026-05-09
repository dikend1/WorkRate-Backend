from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    EmailTokenSchema,
    PasswordResetRequestSchema,
    PasswordResetSchema,
    UserCreateSchema,
    UserResponseSchema,
    TokenSchema,
)
from app.models.user_model import UserModel
from app.core.security import decode_access_token
from app.core.config import settings
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.roles import require_admin
import secrets
import httpx


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
        first_name=data.first_name,
        last_name=data.last_name,
        profile_picture=data.profile_picture,
        current_position=data.current_position,
        current_company_id=data.current_company_id,
        role="user"  # Обычные пользователи регистрируются с ролью user
    )
    return user

@router.post("/confirm-email/request")
async def request_email_confirmation(
    user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.create_email_confirmation_token(user)
    return {
        "message": "Email confirmation token generated",
        "confirmation_token": token
    }

@router.post("/confirm-email", response_model=UserResponseSchema)
async def confirm_email(
    data: EmailTokenSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.confirm_email(data.token)

@router.post("/password-recovery")
async def request_password_recovery(
    data: PasswordResetRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.create_password_reset_token(data.email)
    return {
        "message": "Password reset token generated",
        "reset_token": token
    }

@router.post("/reset-password")
async def reset_password(
    data: PasswordResetSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.reset_password(data.token, data.new_password)
    return {"message": "Password reset"}

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
    user: UserModel = Depends(get_current_user)
):
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

# Google OAuth routes with Authlib
@router.get("/google/login")
async def google_login(request: Request):
    """
    Начинаем OAuth flow:
    1. Генерируем state для CSRF защиты
    2. Сохраняем state в session
    3. Редиректим пользователя на Google
    """
    # Генерируем случайный state для защиты от CSRF
    state = secrets.token_urlsafe(32)
    
    # ВАЖНО: Сохраняем state в session для проверки в callback
    request.session["oauth_state"] = state
    
    # Создаем authorization URL
    authorization_url, _ = oauth_client.create_authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        scope=['openid', 'email', 'profile'],
        state=state  # Передаем наш state
    )
    
    # Редиректим пользователя на Google (НЕ возвращаем JSON!)
    return RedirectResponse(authorization_url)

@router.get("/facebook/login")
async def facebook_login(request: Request):
    if not settings.OAUTH_FACEBOOK_CLIENT_ID or not settings.OAUTH_FACEBOOK_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Facebook OAuth is not configured")

    state = secrets.token_urlsafe(32)
    request.session["facebook_oauth_state"] = state
    facebook_client = AsyncOAuth2Client(
        client_id=settings.OAUTH_FACEBOOK_CLIENT_ID,
        client_secret=settings.OAUTH_FACEBOOK_CLIENT_SECRET,
        redirect_uri="http://localhost:8000/auth/facebook/callback"
    )
    authorization_url, _ = facebook_client.create_authorization_url(
        "https://www.facebook.com/v19.0/dialog/oauth",
        scope=["email", "public_profile"],
        state=state
    )
    return RedirectResponse(authorization_url)

@router.get("/facebook/callback")
async def facebook_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    if not settings.OAUTH_FACEBOOK_CLIENT_ID or not settings.OAUTH_FACEBOOK_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Facebook OAuth is not configured")

    saved_state = request.session.get("facebook_oauth_state")
    if not saved_state or saved_state != state:
        raise HTTPException(status_code=400, detail="State mismatch")
    request.session.pop("facebook_oauth_state", None)

    facebook_client = AsyncOAuth2Client(
        client_id=settings.OAUTH_FACEBOOK_CLIENT_ID,
        client_secret=settings.OAUTH_FACEBOOK_CLIENT_SECRET,
        redirect_uri="http://localhost:8000/auth/facebook/callback"
    )
    token = await facebook_client.fetch_token(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        authorization_response=f"http://localhost:8000/auth/facebook/callback?code={code}&state={state}"
    )
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,email,name", "access_token": access_token}
        )
        user_info = response.json()

    facebook_id = user_info.get("id")
    email = user_info.get("email")
    if not facebook_id or not email:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    query = select(UserModel).where(
        (UserModel.facebook_id == facebook_id) | (UserModel.email == email)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        user = await auth_service.register_user(
            email=email,
            username=email.split("@")[0],
            facebook_id=facebook_id
        )
    elif not user.facebook_id:
        user.facebook_id = facebook_id
        user.is_verified = True
        await db.commit()
        await db.refresh(user)

    token_data = await auth_service.create_token(user)
    request.session["user"] = {"email": user.email, "username": user.username, "id": user.id}
    request.session["access_token"] = token_data["access_token"]
    return RedirectResponse(url="/auth/success", status_code=status.HTTP_302_FOUND)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Callback от Google:
    1. Проверяем state (защита от CSRF)
    2. Обмениваем code на токены (КОД МОЖНО ИСПОЛЬЗОВАТЬ ТОЛЬКО ОДИН РАЗ!)
    3. Получаем информацию о пользователе
    4. Создаем/находим пользователя в БД
    5. ВАЖНО: Редиректим на другую страницу (убираем code из URL!)
    """
    try:
        # ШАГАН 1: Проверяем state для защиты от CSRF атак
        saved_state = request.session.get("oauth_state")
        if not saved_state or saved_state != state:
            raise HTTPException(
                status_code=400,
                detail="State mismatch - возможная CSRF атака. Попробуйте снова."
            )
        
        # Удаляем state из session (больше не нужен)
        request.session.pop("oauth_state", None)
        
        # ШАГ 2: Обмениваем authorization code на токены
        # КРИТИЧЕСКИ ВАЖНО: Код можно использовать ТОЛЬКО ОДИН РАЗ!
        # Если пользователь обновит страницу, код уже будет недействителен
        token = await oauth_client.fetch_token(
            'https://oauth2.googleapis.com/token',
            authorization_response=f'http://localhost:8000/auth/google/callback?code={code}&state={state}'
        )

        if not token or 'access_token' not in token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        access_token = token['access_token']

        # ШАГ 3: Получаем информацию о пользователе через Google API
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_info_url, headers=headers)
            user_info = user_response.json()

        email = user_info.get("email")
        google_id = user_info.get("id")
        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        # ШАГ 4: Ищем или создаем пользователя в БД
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
        elif not user.google_id:
            user.google_id = google_id
            user.is_verified = True
            await db.commit()
            await db.refresh(user)

        # ШАГ 5: Создаем наш JWT токен
        token_data = await auth_service.create_token(user)
        
        # Сохраняем токен и user info в session
        request.session["user"] = {
            "email": user.email,
            "username": user.username,
            "id": user.id
        }
        request.session["access_token"] = token_data["access_token"]
        
        # ШАГ 6: КРИТИЧЕСКИ ВАЖНО!
        # Редиректим на другую страницу, чтобы убрать 'code' из URL
        # Если этого не сделать, при рефреше страницы браузер попытается
        # переиспользовать code, что приведет к ошибке
        return RedirectResponse(
            url="/auth/success",
            status_code=status.HTTP_302_FOUND
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


@router.get("/success")
async def auth_success(request: Request):
    """
    Страница успешной авторизации
    Показывает данные пользователя из session
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "message": "Successfully authenticated!",
        "user": user,
        "access_token": request.session.get("access_token")
    }


    
    
