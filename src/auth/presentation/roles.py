from typing import Callable

from fastapi import HTTPException

from src.auth.domain.entities import UserRoles
from functools import wraps

from src.auth.domain.exceptions import AuthRequired


def check_roles(roles: list[UserRoles]) -> Callable | None:
    if not roles:
        return None

    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            user = kwargs.get("request").get("state").get("user")

            if not user or user.role not in roles:
                raise AuthRequired()

            return await func(*args, **kwargs)

        return wrapped

    return wrapper
