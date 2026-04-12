from src.comments.infrastructure.db.uow import CommentsUnitOfWork


async def collect_comments(game_id: int):
    uow = CommentsUnitOfWork()

    async with uow:
        return await uow.comments.get_all(game_id)
