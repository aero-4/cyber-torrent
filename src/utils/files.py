import aiofiles


async def read_lines(path: str) -> list[str]:
    async with aiofiles.open(path) as file:
        lines = await file.readlines()
    return [i.strip() for i in lines]
