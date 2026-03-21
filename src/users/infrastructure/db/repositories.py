from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.users.domain.entities import UserCreate
from src.users.infrastructure.db.orm import UsersOrm


class PGUsersRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, user: UserCreate) -> UsersOrm:
        obj = await self.session.get(UsersOrm, user.email)

        if obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

        return obj

    async def add(self, user: UserCreate) -> UsersOrm:
        pass
