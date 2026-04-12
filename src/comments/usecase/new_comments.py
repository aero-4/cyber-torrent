from src.comments.domain.entities import CommentCreate
from src.comments.infrastructure.db.uow import CommentsUnitOfWork
from src.users.domain.entities import User
from src.comments.presentation.dtos import CommentCreateDTO


async def add_comment(user: User, data: CommentCreateDTO):
    uow = CommentsUnitOfWork()
    comment_data = CommentCreate(user_id=user.id, **data.model_dump())
    async with uow:
        comment = await uow.comments.add(comment_data)
        await uow.commit()
    return comment
