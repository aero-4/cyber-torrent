from fastapi import APIRouter

from src.games.usecase.collect_games import collect_games

router = APIRouter()


@router.get("/")
async def all_games():
    return await collect_games()