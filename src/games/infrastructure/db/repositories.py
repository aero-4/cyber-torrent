from typing import Type, List

from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import count
from starlette import status

from src.auth.domain.entities import UserCreate, UserUpdate
from src.core.domain.exceptions import NotFound, AlreadyExists
from src.games.domain.entities import GameCreate, Game, GameCollection
from src.games.infrastructure.db.orm import GamesOrm, GamesImagesOrm, GamesTagsOrm
from src.games.presentation.dtos import GamesCollectionDTO
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
            raise NotFound(f"Game '{id}' not found ")

        return obj.to_entity()

    async def get_by_slug(self, slug: str) -> Game:
        stmt = (
            select(GamesOrm)
            .where(GamesOrm.slug == slug)
            .options(
                joinedload(GamesOrm.tags)
            )
        )
        result = await self.session.execute(stmt)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            raise NotFound(message=f"Game '{slug}' not found")
        similar_games = await self.get_by_tags(obj, [i.name for i in obj.tags[:1]])

        return obj.to_entity(similar_games)

    async def get_by_tags(self, obj: Game, tags: list[str], limit: int = 20) -> list[Game]:
        stmt = (
            select(GamesOrm)
            .join(GamesOrm.tags)
            .where(GamesTagsOrm.name.in_(tags),
                   GamesOrm.name != obj.name)
            .options(joinedload(GamesOrm.tags))
            .limit(limit)
            .distinct()
        )

        result = await self.session.execute(stmt)
        games = result.unique().scalars().all()

        if not games:
            raise NotFound(message=f"Games with tags {tags} not found")

        return [game.to_entity() for game in games]

    async def get_all(self, data: GamesCollectionDTO) -> GameCollection:
        stmt = (
            select(GamesOrm)
            .options(
                joinedload(GamesOrm.torrents)
            )
            # .order_by(
            #     GamesOrm.updated_at.desc()
            # )
            .offset(data.offset)
            .limit(data.limit)
        )
        if data.category:
            stmt = stmt.where(GamesOrm.genre == data.category)

        if data.tag:
            stmt = stmt.where(GamesTagsOrm.name == data.tag)

        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()

        stmt2 = select(count(GamesOrm.id))
        if data.category:
            stmt2 = stmt2.where(GamesOrm.genre == data.category)

        if data.tag:
            stmt2 = stmt2.where(GamesTagsOrm.name == data.tag)

        result2 = await self.session.execute(stmt2)
        total_count = result2.scalar_one_or_none()

        return GameCollection(
            games=[i.to_entity() for i in result],
            total_count=total_count
        )

    async def add(self, game: GameCreate) -> Game:
        obj = GamesOrm(**game.model_dump(exclude={"images", "tags"}))
        self.session.add(obj)

        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists(f"Game already exists: {game.name}")

        self.session.add_all([
            GamesImagesOrm(game_id=obj.id, image=i) for i in game.images
        ])

        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists(f"Image already exists")

        self.session.add_all([
            GamesTagsOrm(game_id=obj.id, image=i.image, name=i.name) for i in game.tags
        ])
        try:
            await self.session.flush()
            await self.session.refresh(obj)
        except IntegrityError as e:
            raise AlreadyExists(f"Tag already exists")

        return obj.to_entity()
