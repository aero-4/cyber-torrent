from fastapi import Form, Body
from pydantic import BaseModel, EmailStr


class UserRegisterDTO(BaseModel):
    email: EmailStr = Body(...)
    password: str = Body(...)