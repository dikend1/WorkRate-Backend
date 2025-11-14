from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.routers.router_auth import router as auth_router
import asyncio


app = FastAPI(title="IWork")

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Welcome to IWork "}
