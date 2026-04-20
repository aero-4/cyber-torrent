from src.games.domain.entities import GamesCollection
from src.games.infrastructure.db.uow import GamesUnitOfWork


async def search_games(query: str) -> GamesCollection:
    uow = GamesUnitOfWork()

    async with uow:
        games = await uow.games.get_by_search(query)

    return games
