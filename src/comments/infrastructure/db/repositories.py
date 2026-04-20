from sqlite3 import IntegrityError

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.comments.domain.entities import Comment, CommentCreate, Comments
from src.comments.infrastructure.db.orm import CommentsOrm
from src.core.domain.exceptions import AlreadyExists, NotFound
from src.users.infrastructure.db.orm import UsersOrm


class PGCommentsRepository:

    def __init__(self, session):
        self.session = session

    async def get_all(self, comments_data: Comments) -> list[Comment]:
        stmt = (
            select(CommentsOrm)
            .where(CommentsOrm.game_id == comments_data.game_id)
            .options(joinedload(CommentsOrm.user))
            .order_by(CommentsOrm.created_at.desc())
            .offset(comments_data.offset)
            .limit(comments_data.limit)
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

    async def delete(self, comment_id: int) -> None:
        obj = await self.session.get(CommentsOrm, comment_id)
        if not obj:
            raise NotFound(f'Comment {comment_id} not found ')

        await self.session.delete(obj)
        await self.session.flush()

        return None
