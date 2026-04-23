import pydantic
from pydantic import BaseModel, Field


class ChangePasswordDTO(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=32)
    new_password: str = Field(..., min_length=6, max_length=32)


class UsernameDTO(BaseModel):
    username: str = Field(min_length=5, max_length=32)
