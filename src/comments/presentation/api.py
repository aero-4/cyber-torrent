from fastapi import APIRouter
from starlette.requests import Request

from src.auth.domain.entities import UserRoles
from src.auth.presentation.roles import check_roles
from src.comments.usecase.collect_comments import collect_comments
from src.comments.usecase.new_comments import add_comment
from src.comments.presentation.dtos import CommentCreateDTO

router = APIRouter()


@router.post("/")
@check_roles([UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def to_add_comment(request: Request, dto: CommentCreateDTO):
    return await add_comment(request.state.user, dto)


@router.get("/{game_id}")
@check_roles([UserRoles.USER, UserRoles.ADMIN, UserRoles.SUPER_ADMIN, UserRoles.MANAGER])
async def get_comments(game_id: int):
    return await collect_comments(game_id)
