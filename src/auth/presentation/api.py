from fastapi import APIRouter, Form, Body, Query
from fastapi.responses import RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse

from src.auth.domain.entities import UserRoles
from src.auth.presentation.dependencies import *
from src.auth.presentation.dtos import UserRegisterDTO, UserLoginDTO, UserOtpVerifyDTO
from src.auth.presentation.roles import check_roles
from src.auth.usecase.authentication import authenticate
from src.auth.usecase.auth_qr import *
from src.auth.usecase.confirm_email import confirm_email
from src.auth.usecase.oauth2 import oauth2_google_case, oauth2_yandex_case
from src.auth.usecase.registration import registration
from src.core.config import config
from templates import templates

router = APIRouter()


@router.post("/register", response_model=None)
async def register_user(request: Request,
                        auth: TokenAuthDep,
                        email_provider: EmailProvideDep,
                        auth_form: UserRegisterDTO = Form()):
    status = await registration(auth_form.email, auth_form.password, auth, email_provider)
    if status == "confirm_email":
        return {"message": f"Confirm email. Sent code on '{auth_form.email}'"}
    return {"message": "User registered!"}


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


@router.get("/email/2fa/confirm/{token}")
@check_roles([UserRoles.USER])
async def email_confirm_token_user(request: Request, token: str, email_provider: EmailProvideDep, auth: TokenAuthDep):
    await confirm_email(request.state.user, token, email_provider, auth)
    return {"message": "Email confirmed"}


@router.get("/email/2fa/code/{code}")
@check_roles([UserRoles.NOT_VERIFIED, UserRoles.USER])
async def email_first_confirm_code(request: Request, code: int, email_provider: EmailProvideDep, auth: TokenAuthDep):
    await confirm_email(request.state.user, code, email_provider, auth)
    return {"message": "Email verified"}


@router.get("/oauth2/google")
async def login_user_google(request: Request, oauth2_google: GoogleOauth2ProvideDep, hasher: HasherProvideDep, auth: TokenAuthDep):
    response = RedirectResponse(url=config.app.APP_URI + "/profile")
    auth.response = response

    await oauth2_google_case(request, oauth2_google, hasher, auth)
    return response


@router.get("/oauth2/google/url")
async def get_redirect_uri(oauth2_google: GoogleOauth2ProvideDep):
    url = oauth2_google.generate_redirect_uri()
    return RedirectResponse(url=url)


@router.get("/oauth2/yandex", response_class=HTMLResponse)
async def get_token_page():
    return """
    <html>
        <head><title>Переадресация...</title></head>
        <body>
            <script>
                const hash = window.location.hash.substring(1);
                if (hash) {
                    window.location.href = "/auth/oauth2/yandex/callback?" + hash;
                } else {
                    document.body.innerHTML = "Ошибка: Токен не найден в URL";
                }
            </script>
        </body>
    </html>
    """


@router.get("/oauth2/yandex/callback")
async def login_user_yandex(access_token: str, oauth2_yandex: YandexOauth2ProvideDep, hasher: HasherProvideDep, auth: TokenAuthDep):
    response = RedirectResponse(url=config.app.APP_URI + "/profile")
    auth.response = response
    await oauth2_yandex_case(access_token, oauth2_yandex, hasher, auth)
    return response


@router.get("/oauth2/yandex/url")
async def yandex_redirect_url(oauth_yandex: YandexOauth2ProvideDep):
    url = oauth_yandex.generate_redirect_uri()
    return RedirectResponse(url)

# @router.get("/oauth2/github/callback")
# async def login_user_github(oauth2_github: GitHubProviderDep, hasher: HasherProvideDep, auth: TokenAuthDep):
#     response = RedirectResponse(url=config.app.APP_URI + "/profile")
#     auth.response = response
#     await oauth2_yandex_case(hasher, auth)
#     return response
