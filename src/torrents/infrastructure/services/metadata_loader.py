import asyncio
import logging
from typing import Tuple, Any, Coroutine

import aiohttp
from aiohttp import ClientTimeout

from src.utils.strings import translate_text
from src.core.config import config

logging.basicConfig(level=logging.INFO)


class MetadataParser:
    def __init__(self, api_key: str = config.metadata.RAWGIO_API_TOKEN, concurrency_limit: int = 5):
        self.sem = asyncio.Semaphore(concurrency_limit)

        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api/games"

    async def search(self, page: int) -> Coroutine[Any, Any, tuple[Any]]:
        try:
            results_data = await self.search_games(page)  # search
            translated_data = await self.translate_descriptions_games(results_data)  # translate description
            return translated_data
        except Exception as e:
            logging.error(f"Error load metadata: {e}")

    async def translate_descriptions_games(self, games: list[dict]) -> list[dict]:
        try:
            tasks = [asyncio.create_task(self._translate_description_task(game)) for game in games]
            results: list[dict] = await asyncio.gather(*tasks)
            logging.debug(f"Translated {len(results)} games!")
            return results
        except Exception as e:
            logging.error("Not worked updating description games: %s", e)
        return games

    async def _translate_description_task(self, game_data: dict) -> dict:
        async with self.sem:
            slug = game_data.get("slug")
            if not slug:
                return {}

            try:
                data: dict = await self.get_details(slug)
                desc = data.get("description_raw") if isinstance(data, dict) else data[0].get("description_raw")
                if not desc:
                    raise Exception("Desc not found")

                logging.debug(f"Update new description for game '{slug}': {desc}")
                translated_desc = await translate_text(desc)
                game_data['description_raw'] = translated_desc
                return game_data
            except Exception as e:
                logging.warning(f"Not translate desc '{slug}'. Reason {e}")

            return {}

    async def search_games(self, page: int = 1, max_size: int = 100, platform: str = "1"):
        params = {
            "key": self.api_key,
            "platforms": platform,
            "page_size": max_size,
            "page": page,
        }
        return await self._get_request(params)

    async def get_details(self, slug: str):
        params = {
            "key": self.api_key,
        }
        url = self.base_url + f"/{slug}"
        return await self._get_request(params, url)

    async def _get_request(self, params: dict, url: str = None, timeout: float = 10.0):
        url = url or self.base_url
        async with aiohttp.ClientSession(timeout=ClientTimeout(timeout)) as client:
            try:
                r = await client.get(url, params=params)
                r.raise_for_status()
                data = await r.json()
                return data.get("results", []) if not url else data
            except Exception as e:
                logging.error(f"Fail request for {r.real_url}: {e}")
                return []
