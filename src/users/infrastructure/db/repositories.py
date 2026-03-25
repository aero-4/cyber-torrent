from typing import Type

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.domain.entities import UserCreate
from src.users.infrastructure.db.orm import UsersOrm
from src.users.domain.entities import User


class PGUsersRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> User:
        stmt = select(UsersOrm).where(UsersOrm.id == id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

        return obj.to_entity()

    async def get_by_email(self, email: str) -> User:
        stmt = select(UsersOrm).where(UsersOrm.email == email)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()

        return obj.to_entity()

    async def add(self, user: UserCreate) -> User:
        obj = UsersOrm(**user.model_dump())
        try:
            self.session.add(obj)

            await self.session.flush()
        except IntegrityError as e:
            raise HTTPException(status_code=409,
                                detail="User already exists")
        return obj.to_entity()
