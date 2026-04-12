from pydantic import BaseModel


class Comment(BaseModel):
    game_id: int
    user_id: int
    user: str
    content: str


class CommentCreate(BaseModel):
    game_id: int
    user_id: int
    content: str
