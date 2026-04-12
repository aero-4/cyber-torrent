from fastapi import APIRouter
from starlette.requests import Request

from src.games.usecase.collect_games import collect_games, get_game
from templates import templates

router = APIRouter()


@router.get("/")
async def all_games():
    return await collect_games()


@router.get("/{slug}")
async def get_info_game_slug(slug: str):
    return await get_game(slug)
