from fastapi import APIRouter, Form, Body
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserRegisterDTO, UserLoginDTO
from src.auth.usecase.authentication import authenticate
from src.auth.usecase.registration import registration

router = APIRouter()
csrf_protect = CsrfProtect()
templates = Jinja2Templates(directory="src/auth/presentation/templates")


@router.get("/register")
async def view_login_user(request: Request):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        "form.html", {"request": request, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp


@router.post("/register")
async def register_user(request: Request,
                        auth: TokenAuthDep,
                        auth_form: UserRegisterDTO = Form()):
    if request.cookies.get("fastapi-csrf-token"):
        await csrf_protect.validate_csrf(request)
    await registration(auth_form.email, auth_form.password, auth)
    return {"message": "User registered!"}


@router.post("/login")
async def login_user(login_data: UserLoginDTO,
                     auth: TokenAuthDep):
    await authenticate(login_data, auth)
    return {"message": "User sign up"}


@router.post("/logout")
async def logout_user(auth: TokenAuthDep):
    await auth.unset_tokens_user()
    return {"message": "Logout"}
