import aiohttp

from src.core.config import config
from urllib import parse


class Oauth2Google:

    def generate_redirect_uri(self, client_id: str = config.oauth2.GOOGLE_CLIENT_ID):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": client_id,
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

        return f'{base_url}?{query}'

    async def callback(self, code: str, client_id: str = config.oauth2.GOOGLE_CLIENT_ID, client_secret: str = config.oauth2.GOOGLE_CLIENT_SECRET):
        google_token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": config.app.APP_URI + "/auth/oauth2/google",
            "code": code
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=google_token_url, data=data) as response:
                data = await response.json()
