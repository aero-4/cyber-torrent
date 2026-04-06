import abc


class IOauth2Provider(abc.ABC):

    def generate_redirect_uri(self):
        pass

    async def callback(self, code: str):
        pass
