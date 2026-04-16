from pydantic import BaseModel

from src.core.domain.entities import PageCollection


class GamesCollectionDTO(PageCollection):
    category: str | None = None
    tag: str | None = None