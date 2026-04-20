import asyncio
import logging
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import GameCreate, GameTagsCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents


async def searcher_games() -> None:
    redis = get_redis_client()
    metadata = MetadataParser()
    uow = GamesUnitOfWork()

    page = 0
    try:
        page = await redis.get("metadata_page")
    except:
        pass
    page: int = int(page) + 1 if page else 1

    logging.info(f"RAWGIO: Metadata page: {page}")
    games_result = await metadata.search(page)
    success = 0
    for game in games_result:
        if not game.get("name"):
            continue

        game_data = GameCreate(images=[i["image"] for i in game["short_screenshots"] if game["short_screenshots"] and len(game["short_screenshots"]) > 0],
                               tags=[
                                   GameTagsCreate(name=i["name"],
                                                  image=i["image_background"]) for i in game.get("tags")
                               ],
                               release_date=game.get("released"),
                               name=game["name"],
                               slug=game["slug"],
                               genre=game["genres"][0]["name"],
                               platform=game["platforms"][0]["platform"]["name"],
                               metacritic=game["metacritic"],
                               background_image=game["background_image"],
                               description_raw=game["description_raw"])
        game_obj = None

        async with uow:
            try:
                game_obj = await uow.games.add(game_data)

                success += 1
                logging.info(f"Game added: {game_obj.name}")
                await uow.commit()

            except Exception as e:
                logging.error(f"Game failed: {game["name"]} %s", e)
                await uow.rollback()

        if game_obj:
            await searcher_torrents(game_obj)

    await redis.setex(name="metadata_page", value=page, time=timedelta(minutes=65))

    logging.info(f"Success added games: {success}")
