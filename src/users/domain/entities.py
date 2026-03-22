from pydantic import BaseModel


class User(BaseModel):
    id: int = None
    email: str = None
    password: str = None


class AnonymousUser(User):
    pass
