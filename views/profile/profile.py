from fastapi import APIRouter
from starlette.requests import Request

from src.auth.domain.entities import UserRoles
from src.auth.presentation.roles import check_roles
from templates import templates

router = APIRouter()


@router.get("/profile")
@check_roles(roles=[UserRoles.USER])
async def get_user_profile(request: Request):
    return templates.TemplateResponse(name="profile.html", request=request)
