from sqlite3 import IntegrityError

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.comments.domain.entities import Comment, CommentCreate
from src.comments.infrastructure.db.orm import CommentsOrm
from src.core.domain.exceptions import AlreadyExists
from src.users.infrastructure.db.orm import UsersOrm


class PGCommentsRepository:

    def __init__(self, session):
        self.session = session

    async def get_all(self, game_id: int) -> list[Comment]:
        stmt = (
            select(CommentsOrm).where(CommentsOrm.game_id == game_id)
            .options(joinedload(CommentsOrm.user))
        )
        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()
        return [i.to_entity() for i in result]

    async def add(self, comment: CommentCreate) -> Comment:
        obj = CommentsOrm(**comment.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists()

        return obj.to_entity()
