from fastapi import APIRouter
from starlette.requests import Request

from templates import templates

router = APIRouter()


@router.get("/profile")
async def get_user_profile(request: Request):
    return templates.TemplateResponse(name="profile.html", request=request)
