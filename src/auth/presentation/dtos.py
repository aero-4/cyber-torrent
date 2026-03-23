from fastapi import Form, Body
from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    token_key: str = Field(...)
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")
