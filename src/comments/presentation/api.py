from fastapi import APIRouter
from starlette.requests import Request

from src.auth.domain.entities import UserRoles
from src.auth.presentation.roles import check_roles
from src.comments.usecase.collect_comments import collect_comments
from src.comments.usecase.delete_comment import delete_comment
from src.comments.usecase.new_comments import add_comment
from src.comments.presentation.dtos import CommentCreateDTO, CommentsDTO

router = APIRouter()


@router.post("/")
@check_roles([UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def to_add_comment(request: Request, dto: CommentCreateDTO):
    return await add_comment(request.state.user, dto)


@router.post("/all")
@check_roles([UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def get_comments(request: Request, dto: CommentsDTO):
    return await collect_comments(dto)


@router.delete("/{comment_id}")
@check_roles([UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def to_delete_comment(request: Request, comment_id: int):
    await delete_comment(comment_id)
    return {"message": f"Comment {comment_id} deleted"}
