from slugify import slugify
from googletrans import Translator


def generate_slug(name: str) -> str:
    return slugify(name)


async def translate_text(text: str, dest_lang: str = "ru") -> str:
    async with Translator() as translator:
        return await translator.translate(text, dest=dest_lang)
