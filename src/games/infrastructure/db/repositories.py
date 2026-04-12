from typing import Type

from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from src.auth.domain.entities import UserCreate, UserUpdate
from src.core.domain.exceptions import NotFound, AlreadyExists
from src.games.domain.entities import GameCreate, Game
from src.games.infrastructure.db.orm import GamesOrm, GamesImagesOrm
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

    async def get_by_slug(self, slug: str) -> Game:
        stmt = select(GamesOrm).where(GamesOrm.slug == slug)
        result = await self.session.execute(stmt)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            raise NotFound(message=f"Game '{slug}' not found")

        return obj.to_entity()

    async def get_all(self, offset: int, limit: int) -> list[Game]:
        stmt = (
            select(GamesOrm)
            .options(
                joinedload(GamesOrm.game_images),
                joinedload(GamesOrm.torrents)
            )
            .order_by(
                GamesOrm.updated_at
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()
        return [i.to_entity() for i in result]

    async def add(self, game: GameCreate) -> Game:
        obj = GamesOrm(**game.model_dump(exclude={"images"}))
        self.session.add(obj)

        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists(f"Game already exists: {game.name}")

        self.session.add_all([
            GamesImagesOrm(game_id=obj.id, image=i.image) for i in game.images
        ])

        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists(f"Image already exists")

        return obj.to_entity()
