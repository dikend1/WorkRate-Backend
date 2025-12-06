from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.routers.router_auth import router as auth_router
from app.api.routers.router_companies import router as company_router
from app.api.routers.router_salary import router as salary_router
from app.api.routers.router_reviews import router as review_router
import asyncio


app = FastAPI(title="IWork")

app.include_router(auth_router)
app.include_router(company_router)
app.include_router(salary_router)
app.include_router(review_router)


@app.get("/")
def root():
    return {"message": "Welcome to WorkRate-Backend"}
