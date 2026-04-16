from fastapi import APIRouter

from src.games.presentation.dtos import GamesCollectionDTO
from src.games.usecase.collect_games import collect_games, get_game

router = APIRouter()


@router.post("/")
async def all_games(dto: GamesCollectionDTO):
    return await collect_games(dto)


@router.get("/{slug}")
async def get_info_game_slug(slug: str):
    return await get_game(slug)

