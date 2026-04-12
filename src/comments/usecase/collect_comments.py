from src.comments.infrastructure.db.uow import CommentsUnitOfWork
from src.comments.presentation.dtos import CommentsDTO


async def collect_comments(comments_data: CommentsDTO):
    uow = CommentsUnitOfWork()

    async with uow:
        return await uow.comments.get_all(comments_data)
