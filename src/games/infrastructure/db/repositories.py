import random
from typing import Type, List

from fastapi import HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.functions import count
from starlette import status

from src.auth.domain.entities import UserCreate, UserUpdate
from src.core.domain.exceptions import NotFound, AlreadyExists
from src.games.domain.entities import GameCreate, Game, GamesCollection
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
        obj: Game | None = result.unique().scalar_one_or_none()
        if not obj:
            raise NotFound(message=f"Game '{slug}' not found")

        similar_games = None
        try:
            tag = random.choice(obj.tags)
            similar_games = await self.get_by_tags(obj, tag.name)
        except:
            pass
        return obj.to_entity(similar_games)

    async def get_by_tags(self, obj: Game, tag: str, limit: int = 20) -> list[Game]:
        stmt = (
            select(GamesOrm)
            .join(GamesOrm.tags)
            .where(GamesOrm.name != obj.name,
                   GamesTagsOrm.name == tag)
            .group_by(GamesOrm.id)
            .order_by(func.count(GamesTagsOrm.id).desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        games = result.unique().scalars().all()

        if not games:
            raise NotFound(message=f"Games with tags {tag} not found")

        return [game.to_entity() for game in games]

    async def get_all(self, data: GamesCollectionDTO) -> GamesCollection:
        stmt = (
            select(GamesOrm)
            .options(
                joinedload(GamesOrm.torrents),
                joinedload(GamesOrm.tags)
            )
            .order_by(
                GamesOrm.created_at.desc()
            )
            .offset(data.offset)
            .limit(data.limit)
        )

        if data.category and data.category.isdigit():
            stmt = stmt.where(GamesOrm.release_date.icontains(data.category))

        elif data.category and not data.category.isdigit():
            stmt = stmt.where(GamesOrm.genre == data.category)


        if data.tag:
            stmt = stmt.where(GamesOrm.tags.any(GamesTagsOrm.name == data.tag))

        if data.query:
            stmt = stmt.where(GamesOrm.name.icontains(data.query))

        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()

        count_stmt = select(count(GamesOrm.id))
        if data.category:
            count_stmt = count_stmt.where(or_(GamesOrm.genre == data.category,
                                              GamesOrm.release_date.icontains(data.category)))

        if data.tag:
            count_stmt = count_stmt.where(GamesOrm.tags.any(GamesTagsOrm.name == data.tag))

        if data.query:
            count_stmt = count_stmt.where(GamesOrm.name.icontains(data.query))

        result2 = await self.session.execute(count_stmt)
        total_count = result2.scalar_one()

        return GamesCollection(
            games=[i.to_entity() for i in result],
            total_count=total_count or 0
        )

    async def get_by_search(self, query: str) -> GamesCollection:
        stmt = select(GamesOrm).where(
            GamesOrm.name.icontains(query)
        )
        result = await self.session.execute(stmt)
        result = result.unique().scalars().all()

        count_stmt = select(count(GamesOrm.id))

        result2 = await self.session.execute(count_stmt)
        total_count = result2.scalar_one()

        return GamesCollection(
            games=[i.to_entity() for i in result],
            total_count=total_count or 0
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
