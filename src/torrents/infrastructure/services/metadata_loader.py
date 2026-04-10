import asyncio
import logging
import aiohttp

from src.utils.strings import translate_text
from src.core.config import config

logging.basicConfig(level=logging.INFO)


class MetadataParser:
    def __init__(self, api_key: str):
        self.base_url = "https://api.rawg.io/api/games"
        self.api_key = api_key

    async def search(self):
        page = 1
        result = []

        while True:
            try:
                results_data = await self.search_games(page)

                if len(results_data) == 0:
                    logging.info(f"Page: {page} FINISH!")
                    return result

                result.append(results_data)
            except Exception as e:
                logging.error(f"Error load metadata: {e}")
            await asyncio.sleep(1)
            page += 1



    async def update_desc(self, games):
        try:
            logging.info(f"Length: {len(games)}")
            for game in games:
                try:
                    data = await self.get_details(game.slug)
                    desc = data["description_raw"]
                    game.description = desc
                    await game.save()
                    logging.info(f"Set NEW desc - {desc}")
                except Exception as e:
                    logging.warning(f"Not translate this desc - {game}. Reason {e}")
        except Exception as e:
            logging.error("Not work update desc")

    async def search_games(self, page: int = 1):
        params = {
            "key": self.api_key,
            "platforms": "1",
            "page_size": 80,
            "page": page,
        }
        return await self._get(params)

    async def get_details(self, slug: str):
        params = {
            "key": self.api_key,
        }
        url = self.base_url + f"/{slug}"
        return await self._get(params, url)

    async def _get(self, params: dict, url: str = None):
        async with aiohttp.ClientSession(timeout=10) as client:
            try:
                r = await client.get(url or self.base_url,
                                     params=params)
                r.raise_for_status()

                data = await r.json()
                return data.get("results", []) if not url else data
            except Exception as e:
                logging.error(f"Fail request {params}: {e}")
                return []
