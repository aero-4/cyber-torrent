from fastapi import APIRouter, Form, Body
from fastapi.responses import RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.responses import FileResponse

from src.auth.infrastructure.providers.oauth2_google import Oauth2Google
from src.auth.presentation.dependencies import TokenAuthDep, HasherProvideDep, QrProvideDep, EmailProvideDep, Oauth2ProvideDep
from src.auth.presentation.dtos import UserRegisterDTO, UserLoginDTO, UserOtpVerifyDTO
from src.auth.usecase.authentication import authenticate
from src.auth.usecase.auth_qr import *
from src.auth.usecase.confirm_email import email_send_token, confirm_email
from src.auth.usecase.registration import registration
from templates import templates

router = APIRouter()
csrf_protect = CsrfProtect()


@router.get("/register")
async def view_register_user(request: Request):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        name="register.html", request=request
    )
    csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp


@router.post("/register", response_model=None)
async def register_user(request: Request,
                        auth: TokenAuthDep,
                        auth_form: UserRegisterDTO = Form()):
    # try:
    #     if request.cookies.get("fastapi-csrf-token"):
    #         await csrf_protect.validate_csrf(request)
    # except Exception as e:
    #     pass
    await registration(auth_form.email, auth_form.password, auth)
    return {"message": "User registered!"}


@router.get("/login")
async def login_user(request: Request):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        name="login.html", request=request
    )
    csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp


@router.post("/login")
async def login_user(
        auth: TokenAuthDep,
        hasher_provider: HasherProvideDep,
        qr_code_provider: QrProvideDep,
        login_data: UserLoginDTO = Form(...),

):
    await authenticate(login_data, auth, hasher_provider, qr_code_provider)
    return {"message": "User sign up"}


@router.post("/logout")
async def logout_user(auth: TokenAuthDep):
    await auth.unset_tokens_user()
    return {"message": "Logout"}


@router.post("/refresh")
async def refresh_token(auth: TokenAuthDep):
    await auth.refresh_access_token()
    return {"message": "Token refreshed"}


@router.post("/otp/confirm")
async def qr_code_auth(otp_form: UserOtpVerifyDTO = Form()):
    await authenticate_opt_code(otp_form.otp_code, otp_form.email)
    return {"message": "Otp verify confirm"}


@router.post("/otp/qr")
async def qr_code(email: str = Form(..., description="Email required for qr auth")):
    qr_path = generate_qr_code(email)
    return FileResponse(qr_path)


@router.post("/email/sent")
async def email_sent_email_token(email_provider: EmailProvideDep, email: str = Form(..., description="Email for confirm")):
    await email_send_token(email, email_provider)
    return {"message": f"Sent on email {email}"}


@router.get("/email/confirm/{token}")
async def email_confirm_token_user(token: str, email_provider: EmailProvideDep):
    await confirm_email(token, email_provider)
    return {"message": "Email confirmed"}


@router.get("/oauth2/google")
async def get_redirect_uri(request: Request, oauth2_google: Oauth2ProvideDep):
    print(request.query_params)
    await oauth2_google.callback(request.query_params.get("code"))
    return templates.TemplateResponse(name="user.html", request=request)


@router.get("/oauth2/google/url")
async def get_redirect_uri(oauth2_google: Oauth2ProvideDep):
    url = oauth2_google.generate_redirect_uri()
    return RedirectResponse(url=url)


@router.post("/oauth2/google/callback")
async def check_callback_google(oauth2_google: Oauth2ProvideDep, code: str = Body(..., embed=True)):
    return
