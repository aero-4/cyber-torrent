from fastapi import APIRouter

from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserRegisterDTO
from src.auth.usecase.registration import registration

router = APIRouter()


@router.post("/register")
async def register_user(user_data: UserRegisterDTO, auth: TokenAuthDep):
    await registration(user_data, auth)
    return {"message": "User registered!"}


@router.post("/login")
async def login_user():
    return {"message": "User login"}


@router.post("/refresh")
async def refresh_token():
    pass


@router.post("/logout")
async def logout_user():
    pass
