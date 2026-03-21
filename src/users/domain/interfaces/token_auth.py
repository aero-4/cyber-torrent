import abc

from src.users.infrastructure.db.orm import UsersOrm


class ITokenAuth(abc.ABC):

    @abc.abstractmethod
    def read_token(self):
        pass

    @abc.abstractmethod
    def set_tokens(self, user: UsersOrm):
        pass
