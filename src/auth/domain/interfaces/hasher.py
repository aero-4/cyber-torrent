import abc


class IHasherProvider(abc.ABC):

    @abc.abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        pass

    @abc.abstractmethod
    def hash_password(self, password: str) -> str:
        pass
