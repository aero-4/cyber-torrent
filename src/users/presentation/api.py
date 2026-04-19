from fastapi import APIRouter, File, UploadFile, Body
from starlette.requests import Request
from starlette.responses import FileResponse

from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.presentation.dependencies import TokenAuthDep, HasherProvideDep
from src.auth.presentation.roles import check_roles, UserRoles
from src.users.presentation.dtos import ChangePasswordDTO
from src.users.usecase.change_password_user import change_password_user
from src.users.usecase.edit_avatar import edit_new_avatar
from templates import templates

router = APIRouter()


@router.get("/me")
@check_roles(roles=[UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def get_me(request: Request):
    return request.state.user.model_dump(
        exclude={
            "password",
            "id"
        }
    )


@router.patch("/avatar")
@check_roles(roles=[UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def edit_avatar(file: UploadFile, request: Request):
    file_path = await edit_new_avatar(file, request.state.user)
    return FileResponse(file_path)


@router.patch("/change-password")
@check_roles(roles=[UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def patch_change_password(request: Request, password: ChangePasswordDTO, auth: TokenAuthDep, hasher: HasherProvideDep):
    await change_password_user(request.state.user, password, hasher, auth)
    return {"message": "Password changed"}
