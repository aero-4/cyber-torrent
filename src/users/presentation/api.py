from fastapi import APIRouter
from starlette.requests import Request

from src.auth.presentation.roles import check_roles, UserRoles

router = APIRouter()


@router.get("/me")
@check_roles(roles=[UserRoles.USER])
async def get_me(request: Request):
    return request.state.user.model_dump(
        exclude={
            "password"
        }
    )
