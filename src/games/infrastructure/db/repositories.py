from typing import Type

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.domain.entities import UserCreate, UserUpdate
from src.core.domain.exceptions import NotFound
from src.games.domain.entities import GameCreate, Game
from src.games.infrastructure.db.orm import GamesOrm
from src.users.infrastructure.db.orm import UsersOrm
from src.users.domain.entities import User


class PGGamesRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Game:
        stmt = select(GamesOrm).where(UsersOrm.id == id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

        return obj.to_entity()

    async def get_all(self) -> list[Game]:
        stmt = select(GamesOrm)
        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()
        return [i.to_entity() for i in result]

    async def add(self, game: GameCreate) -> Game:
        obj = GamesOrm(**game.model_dump())
        try:
            self.session.add(obj)

            await self.session.flush()
        except IntegrityError as e:
            print(e)
            raise HTTPException(status_code=409,
                                detail="Game already exists")
        return obj.to_entity()
