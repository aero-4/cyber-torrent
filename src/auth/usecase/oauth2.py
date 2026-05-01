import secrets

from starlette.requests import Request

from src.games.infrastructure.services.files_downloader import ImagesDownloader
from src.auth.domain.entities import UserCreate, UserRoles
from src.auth.domain.interfaces.hasher import IHasherProvider
from src.auth.domain.interfaces.oauth2 import IOauth2Provider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.core.domain.exceptions import BadRequest
from src.users.infrastructure.db.uow import UsersUnitOfWork

downloader = ImagesDownloader()
uow = UsersUnitOfWork()


async def oauth2_google_case(request: Request, oauth2_google: IOauth2Provider, hasher: IHasherProvider, auth: ITokenAuth, ):
    data = await oauth2_google.callback(request.query_params.get("code"))

    password = secrets.token_urlsafe(16)
    hashed_password = hasher.hash_password(password)
    email = data['email']
    username = data["name"]
    avatar_image = await downloader.save_one_image(data["picture"])

    async with uow:
        user = await uow.users.get_by_email(email=email)

        if not user:
            user_data = UserCreate(email=email,
                                   username=username,
                                   password=hashed_password,
                                   avatar_image=avatar_image,
                                   is_verify_email=data["email_verified"],
                                   role=UserRoles.USER)
            user = await uow.users.add(user_data)
            await uow.commit()

        await auth.set_tokens(user)


async def oauth2_yandex_case(access_token: str, oauth2_yandex: IOauth2Provider, hasher: IHasherProvider, auth: ITokenAuth):
    data = await oauth2_yandex.callback(access_token)

    password = secrets.token_urlsafe(16)
    hashed_password = hasher.hash_password(password)
    email = data.get('default_email')
    username = data.get("login") or data.get("display_name")
    default_avatar_id = data.get("default_avatar_id") or "50595/0h-3"
    avatar_image = f"https://avatars.mds.yandex.net/get-yapic/{default_avatar_id}"
    avatar_image = await downloader.save_one_image(avatar_image)

    user_data = UserCreate(email=email,
                           password=hashed_password,
                           username=username,
                           avatar_image=avatar_image,
                           is_verify_email=len(email) > 0,
                           role=UserRoles.USER)

    async with uow:
        user = await uow.users.get_by_email(email=email)

        if not user:
            user = await uow.users.add(user_data)
            await uow.commit()

        await auth.set_tokens(user)
