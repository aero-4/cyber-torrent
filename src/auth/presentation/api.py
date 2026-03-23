from fastapi import APIRouter, Form
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserRegisterDTO
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
                        email: str = Form(...),
                        password: str = Form(...)):
    if request.cookies.get("fastapi-csrf-token"):
        await csrf_protect.validate_csrf(request)
        await registration(email, password, auth)
        return {"message": "User registered!"}


@router.post("/login")
async def login_user():
    return {"message": "User login"}


@router.post("/logout")
async def logout_user():
    pass
