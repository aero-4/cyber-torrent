from urllib import parse

import aiohttp

from src.auth.domain.interfaces.oauth2 import IOauth2Provider
from src.auth.domain.interfaces.token_auth import ITokenProvider
from src.core.config import config


class Oauth2Yandex(IOauth2Provider):

    def __init__(self, token_provider: ITokenProvider, client_id: str = config.oauth2.YANDEX_CLIENT_ID, client_secret: str = config.oauth2.YANDEX_CLIENT_SECRET):
        super().__init__(token_provider)

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_provider = token_provider

    def generate_redirect_uri(self) -> str:
        base_url = "https://oauth.yandex.ru/authorize"
        params = {
            "response_type": "token",
            "client_id": self.client_id
        }

        query = parse.urlencode(params, quote_via=parse.quote)
        return f'{base_url}?{query}'

    async def callback(self, token: str):
        url = f"https://login.yandex.ru/info"
        params = {
            "format": "json",
            "jwt_secret": self.client_secret
        }
        headers = {
            "Authorization": f"OAuth {token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
        return data
