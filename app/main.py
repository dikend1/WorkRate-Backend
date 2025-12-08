from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.routers.router_auth import router as auth_router
from app.api.routers.router_companies import router as company_router
from app.api.routers.router_salary import router as salary_router
from app.api.routers.router_reviews import router as review_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
import asyncio


app = FastAPI(title="IWork")

# КРИТИЧЕСКИ ВАЖНО: Добавляем CORS middleware
# Без этого браузер заблокирует запросы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ВАЖНО: Добавляем SessionMiddleware для работы OAuth2
# Это нужно для хранения state и user информации между запросами
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,  # Используем тот же SECRET_KEY из .env
    max_age=3600 * 24 * 7,  # Session живет 7 дней
    https_only=False  # В production поставьте True
)

app.include_router(auth_router)
app.include_router(company_router)
app.include_router(salary_router)
app.include_router(review_router)


@app.get("/")
def root():
    return {"message": "Welcome to WorkRate-Backend"}
