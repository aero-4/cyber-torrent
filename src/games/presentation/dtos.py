from pydantic import BaseModel

from src.core.domain.entities import PageCollection


class GamesCollectionDTO(PageCollection):
    category: str | int | None = None
    tag: str | None = None
    query: str | None = None
    year: int | None = None