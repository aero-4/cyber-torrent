from pydantic import BaseModel, Field

from src.core.domain.entities import PageCollection


class GamesCollectionDTO(PageCollection):
    category: str | None = None
    tag: str | None = None
    query: str | None = Field(None, min_length=1)
    year: int | None = None
