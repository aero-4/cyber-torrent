from src.db.engine import async_session_maker
from src.games.infrastructure.db.repositories import PGGamesRepository


class GamesUnitOfWork:

    async def __aenter__(self):
        self.session = async_session_maker()
        self.games = PGGamesRepository(self.session)

    async def __aexit__(self, *args):
        await self.session.rollback()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
