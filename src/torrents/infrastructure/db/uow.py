


from src.db.engine import async_session_maker
from src.torrents.infrastructure.db.repositories import PGTorrentsRepository
from src.users.infrastructure.db.repositories import PGUsersRepository


class TorrentsUnitOfWork:

    async def __aenter__(self):
        self.session = async_session_maker()
        self.torrents = PGTorrentsRepository(self.session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
