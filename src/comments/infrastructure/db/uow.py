from src.comments.infrastructure.db.repositories import PGCommentsRepository
from src.db.engine import async_session_maker


class CommentsUnitOfWork:

    async def __aenter__(self):
        self.session = async_session_maker()
        self.comments = PGCommentsRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()

    async def rollback(self):
        await self.session.rollback()

    async def commit(self):
        await self.session.commit()
