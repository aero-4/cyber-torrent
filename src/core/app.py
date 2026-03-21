from fastapi import FastAPI

from src.users.presentation.router import users_router

app = FastAPI()

app.include_router(router=users_router, prefix="/api/users")