import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from src.auth.domain.entities import UserUpdate
from src.users.domain.entities import User
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def edit_new_avatar(avatar: UploadFile, user: User) -> str:
    uow = UsersUnitOfWork()

    random_name = Path(f"static/uploads/{uuid.uuid4()}.jpeg")

    async with aiofiles.open(random_name, "wb") as file:
        bytes = await avatar.read()
        await file.write(bytes)

    async with uow:
        update_data = UserUpdate(id=user.id,
                                 avatar_image=str(random_name))
        await uow.users.update(update_data)
        await uow.commit()

    return str(random_name)
