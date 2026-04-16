from src.games.domain.entities import Game
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.presentation.dtos import GamesCollectionDTO


async def collect_games(dto: GamesCollectionDTO) -> list[Game]:
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_all(dto)
    return games


async def get_game(slug: str) -> Game:
    uow = GamesUnitOfWork()
    async with uow:
        game = await uow.games.get_by_slug(slug)
    return game


async def get_games_by_category(category: str):
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_by_cat(category)
    return games
