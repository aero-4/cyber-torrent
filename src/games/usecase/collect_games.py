from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.presentation.dtos import GamesCollectionDTO


async def collect_games(dto: GamesCollectionDTO):
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_all(dto.offset, dto.limit)
    return games


async def get_game(slug: str):
    uow = GamesUnitOfWork()

    async with uow:
        game = await uow.games.get_by_slug(slug)
    return game
