from fastapi import APIRouter
from starlette.requests import Request

from src.users.infrastructure.db.uow import UsersUnitOfWork
from src.users.presentation.dependencies import TokenAuthDep
from src.users.presentation.dtos import UserRegisterDTO
from src.users.usecase.registration import registration

users_router = APIRouter()


@users_router.post("/register")
async def register_user(user_data: UserRegisterDTO,
                        auth: TokenAuthDep):
    await registration(user_data, auth)
    return {"message": "User registered!"}


@users_router.post("/login")
async def login_user():
    return {"message": "User login"}


@users_router.post("/refresh")
async def refresh_token():
    pass


@users_router.post("/logout")
async def logout_user():
    pass
