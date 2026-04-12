from src.games.infrastructure.db.uow import GamesUnitOfWork


async def collect_games():
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_all()

    return games


async def get_game(slug: str):
    uow = GamesUnitOfWork()

    async with uow:
        game = await uow.games.get_by_slug(slug)

    return game
