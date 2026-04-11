from src.games.infrastructure.db.uow import GamesUnitOfWork


async def collect_games():
    uow = GamesUnitOfWork()
    async with uow:
        games = await uow.games.get_all()

    print(games)
    return games