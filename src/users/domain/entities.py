from pydantic import BaseModel


class User(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    role: int = None
    is_verify_otp: bool = False


class AnonymousUser(User):
    pass
