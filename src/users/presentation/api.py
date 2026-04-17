from fastapi import APIRouter, File, UploadFile
from starlette.requests import Request
from starlette.responses import FileResponse

from src.auth.presentation.roles import check_roles, UserRoles
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
async def edit_avatar(file: UploadFile, request: Request):
    file_path = await edit_new_avatar(file, request.state.user)
    return FileResponse(file_path)
