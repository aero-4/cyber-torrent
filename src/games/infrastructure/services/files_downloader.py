import asyncio
import uuid

import aiofiles
import aiohttp
from aiohttp import StreamReader


class ImagesDownloader:

    async def save_some_images(self, links: list[str]) -> list[str]:
        return await asyncio.gather(
            *[
                self.save_one_image(i) for i in links
            ]
        )

    async def save_one_image(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await self.save_file(response.content, prefix=url.split(".")[-1])

    async def save_file(self, content: StreamReader, prefix: str) -> str:
        path = self._path_file(prefix)
        async with aiofiles.open(path, "wb") as file:
            async for chunk in content.iter_chunked(65536):
                await file.write(chunk)
        return path

    def _path_file(self, prefix: str = "png") -> str:
        name = str(uuid.uuid4())
        return f'static/images/{name}.{prefix}'
