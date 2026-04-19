from pydantic import BaseModel


class User(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    role: int = None
    avatar_image: str | None = None
    is_verify_otp: bool = False
    otp_secret: str | None = None
    is_verify_email: bool = False


class AnonymousUser(User):
    pass
