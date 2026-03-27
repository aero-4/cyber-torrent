from fastapi import APIRouter, Form, Body
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.responses import Response, FileResponse
from starlette.templating import Jinja2Templates

from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserRegisterDTO, UserLoginDTO
from src.auth.usecase.authentication import authenticate, generate_qr_code, authenticate_with_qr
from src.auth.usecase.registration import registration
from templates.templates import templates

router = APIRouter()
csrf_protect = CsrfProtect()


@router.get("/register")
async def view_register_user(request: Request):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        "register.html", {"request": request, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp


@router.post("/register")
async def register_user(request: Request,
                        auth: TokenAuthDep,
                        auth_form: UserRegisterDTO = Form()):
    try:
        if request.cookies.get("fastapi-csrf-token"):
            await csrf_protect.validate_csrf(request)
    except Exception as e:
        pass
    await registration(auth_form.email, auth_form.password, auth)
    return {"message": "User registered!"}


@router.get("/qr?token={token}")
async def qr_code_auth(token: str):
    return await authenticate_with_qr(token)


@router.get("/qr")
async def qr_code():
    qr_data = await generate_qr_code()
    return Response(
        content=qr_data,
        media_type="image/png"
    )


@router.get("/login")
async def login_user(request: Request):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        "login.html", {"request": request, "csrf_token": csrf_token}
    )
    csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp


@router.post("/login")
async def login_user(login_data: UserLoginDTO,
                     auth: TokenAuthDep):
    await authenticate(login_data, auth)
    return {"message": "User sign up"}


@router.post("/logout")
async def logout_user(auth: TokenAuthDep):
    await auth.unset_tokens_user()
    return {"message": "Logout"}


@router.post("/refresh")
async def refresh_token(auth: TokenAuthDep):
    await auth.refresh_access_token()
    return {"message": "Token refreshed"}
