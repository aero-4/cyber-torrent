import asyncio
import logging
from datetime import timedelta

from src.core.infrastructure.redis import get_redis_client
from src.games.domain.entities import GameCreate, GameTagsCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.infrastructure.services.files_downloader import ImagesDownloader
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents


async def searcher_games(start_page: int = 1) -> None:
    redis = get_redis_client()
    metadata = MetadataParser()
    uow = GamesUnitOfWork()
    images_provider = ImagesDownloader()

    page = start_page
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

        short_local_screens = await images_provider.save_some_images([i.get("image") for i in game["short_screenshots"]])
        local_background_image = await images_provider.save_one_image(game["background_image"])

        game_data = GameCreate(images=short_local_screens,
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
                               background_image=local_background_image,
                               description_raw=game["description_raw"])
        game_obj = None

        async with uow:
            try:
                game_obj = await uow.games.add(game_data)

                success += 1
                logging.info(f"Game added: %s", game_obj.name)
                await uow.commit()

            except Exception as e:
                logging.error(f"Game failed: %s %s", (game["name"], e))
                await uow.rollback()

        if game_obj:
            await searcher_torrents(game_obj)

    await redis.setex(name="metadata_page", value=page, time=timedelta(minutes=65))

    logging.info(f"Success added games: {success}")
