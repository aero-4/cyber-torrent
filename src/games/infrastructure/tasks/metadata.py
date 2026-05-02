import logging

from src.games.infrastructure.services.redis_cache import RedisCache
from src.games.domain.entities import GameCreate, GameTagsCreate
from src.games.infrastructure.db.uow import GamesUnitOfWork
from src.games.infrastructure.services.files_downloader import ImagesDownloader
from src.torrents.infrastructure.services.metadata_loader import MetadataParser
from src.torrents.infrastructure.tasks.torrent import searcher_torrents


async def searcher_games() -> None:
    redis = RedisCache()
    metadata = MetadataParser()
    uow = GamesUnitOfWork()
    images_provider = ImagesDownloader()
    page = await redis.increment()
    logging.info(f"[RAWGIO]: Metadata page: {page}")
    games_result = await metadata.search(page)
    success = 0
    async with uow:
        for game in games_result:
            if not game.get("name"):
                continue

            try:
                if await uow.games.get_by_slug(game["slug"]):
                    logging.warning("Game '%r' already exists", game["slug"])
                    continue
            except:
                pass

            short_local_screens = await images_provider.save_some_images([i.get("image") for i in game["short_screenshots"] if not "/media/games/" in i.get("image")])
            local_background_image = await images_provider.save_one_image(game["background_image"])
            tags = [
                GameTagsCreate(name=i["name"],
                               image=i["image_background"]) for i in game.get("tags")
            ]
            game_data = GameCreate(images=short_local_screens,
                                   tags=tags,
                                   release_date=game.get("released"),
                                   name=game["name"],
                                   slug=game["slug"],
                                   genre=game["genres"][0]["name"],
                                   platform=game["platforms"][0]["platform"]["name"],
                                   metacritic=game["metacritic"],
                                   background_image=local_background_image,
                                   description_raw=game["description_raw"])
            game_obj = None

            try:
                game_obj = await uow.games.add(game_data)
                await uow.commit()

                success += 1
                logging.info(f"Game added: %r", game_obj.name)

            except Exception as e:
                logging.error(f"Game failed: %r %r", game["name"], e)
                await uow.rollback()

            if game_obj:
                await searcher_torrents(game_obj)

    logging.info(f"Success added games: {success}")
