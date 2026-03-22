import abc

from src.auth.domain.entities import TokenType
from src.users.infrastructure.db.orm import UsersOrm


class ITokenAuth(abc.ABC):


    @abc.abstractmethod
    async def read_token(self, token_type: TokenType):
        pass

    @abc.abstractmethod
    async def set_tokens(self, user: UsersOrm):
        pass
