from pydantic import BaseModel


class CommentCreateDTO(BaseModel):
    game_id: int
    content: str
