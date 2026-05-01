from pathlib import Path
import asyncio
import uuid

import aiofiles
import aiohttp
from aiohttp import StreamReader


class ImagesDownloader:
    def __init__(
            self,
            static_dir: Path | str = Path("static/uploads"),
            public_prefix: str = "/static/uploads",
    ):
        self.static_dir = Path(static_dir)
        self.public_prefix = public_prefix
        self.static_dir.mkdir(parents=True, exist_ok=True)

    async def save_some_images(self, links: list[str]) -> list[str]:
        return await asyncio.gather(*(self.save_one_image(url) for url in links))

    async def save_one_image(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()

                ext = self._guess_extension(response, url)
                filename = self._file_name(ext)

                return await self.save_file(response.content, filename)

    async def save_file(
            self,
            content: StreamReader,
            filename: str,
            _chunk: int = 65536,
    ) -> str:
        file_path = self.static_dir / filename

        async with aiofiles.open(file_path, "wb") as file:
            async for chunk in content.iter_chunked(_chunk):
                await file.write(chunk)

        return f"{self.public_prefix}/{filename}"

    def _file_name(self, ext: str) -> str:
        name = uuid.uuid4().hex
        return f"{name}.{ext}"

    def _guess_extension(self, response: aiohttp.ClientResponse, url: str) -> str:
        content_type = response.headers.get("Content-Type", "").lower()

        if "png" in content_type:
            return "png"
        if "jpeg" in content_type or "jpg" in content_type:
            return "jpg"
        if "webp" in content_type:
            return "webp"
        if "gif" in content_type:
            return "gif"

        suffix = Path(url.split("?", 1)[0]).suffix.lstrip(".")
        return suffix or "bin"
