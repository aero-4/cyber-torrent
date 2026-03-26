from pydantic import BaseModel


class User(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    role: int = None


class AnonymousUser(User):
    pass
