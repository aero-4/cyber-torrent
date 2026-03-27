from src.core.domain.exceptions import AlreadyExists


class UserAlreadyExists(AlreadyExists):
    message = "Email already exists"
