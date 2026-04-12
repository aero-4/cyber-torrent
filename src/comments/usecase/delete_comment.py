from src.comments.infrastructure.db.uow import CommentsUnitOfWork


async def delete_comment(comment_id: int):
    uow = CommentsUnitOfWork()

    async with uow:
        return await uow.comments.delete(comment_id)