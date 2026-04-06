import aiohttp

from src.auth.domain.interfaces.oauth2 import IOauth2Provider
from src.auth.domain.interfaces.token_auth import ITokenProvider
from src.core.config import config
from urllib import parse

from src.core.domain.exceptions import BadRequest


class Oauth2Google(IOauth2Provider):

    def __init__(self, token_provider: ITokenProvider, client_id: str = config.oauth2.GOOGLE_CLIENT_ID, client_secret: str = config.oauth2.GOOGLE_CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_provider = token_provider

    def generate_redirect_uri(self):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": self.client_id,
            "redirect_uri": f"{config.app.APP_URI}/auth/oauth2/google",
            "response_type": "code",
            "scope": " ".join([
                "openid",
                "profile",
                "email"
            ]),
            # "access_type": "offline",
            # "state": ""
        }
        query = parse.urlencode(params, quote_via=parse.quote)

        print(f'{base_url}?{query}')

        return f'{base_url}?{query}'

    async def callback(self, code: str):
        google_token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": config.app.APP_URI + "/auth/oauth2/google",
            "code": code
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=google_token_url, data=data) as response:
                response.raise_for_status()
                data = await response.json()
                print(data)

        return self._parse_data_id_token(data)

    def _parse_data_id_token(self, data: dict):
        id_token = data.get("id_token")
        if not id_token:
            raise BadRequest(message="No id_token in response")

        try:
            id_data = self.token_provider.decode_jwt_without_secret(id_token)
        except Exception as e:
            raise BadRequest(message="Unreadable google-user data")

        return id_data
