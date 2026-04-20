import datetime

from pydantic import BaseModel


class Comment(BaseModel):
    game_id: int
    user_id: int
    user: str
    user_avatar: str
    content: str
    created_at: datetime.datetime


class CommentCreate(BaseModel):
    game_id: int
    user_id: int
    content: str


class Comments(BaseModel):
    game_id: int
    offset: int = 0
    limit: int = 20