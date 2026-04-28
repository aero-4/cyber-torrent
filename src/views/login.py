from fastapi import APIRouter
from starlette.requests import Request

# from src.core.app import csrf_protect
from templates import templates

router = APIRouter()


@router.get("/login")
async def login_user(request: Request):
    # csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    resp = templates.TemplateResponse(
        name="login.html", request=request
    )
    # csrf_protect.set_csrf_cookie(signed_token, resp)
    return resp
