from pydantic import BaseModel

from src.core.domain.entities import PageCollection


class CommentCreateDTO(BaseModel):
    game_id: int
    content: str


class CommentsDTO(PageCollection):
    game_id: int
