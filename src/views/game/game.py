from fastapi import APIRouter
from starlette.requests import Request

from templates import templates

router = APIRouter(tags=["Game views"])


@router.get("/game/{slug}")
async def get_game(request: Request):
    return templates.TemplateResponse(request=request, name="game.html")
