import secrets

from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.auth.domain.entities import UserCreate
from src.auth.domain.interfaces.hasher import IHasherProvider
from src.auth.domain.interfaces.oauth2 import IOauth2Provider
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.core.domain.exceptions import BadRequest
from src.users.infrastructure.db.uow import UsersUnitOfWork


async def oauth2_google_case(request: Request, oauth2_google: IOauth2Provider, hasher: IHasherProvider, auth: ITokenAuth):
    uow = UsersUnitOfWork()
    code = request.query_params.get("code")

    if not code:
        raise BadRequest("No code in query params")

    data = await oauth2_google.callback(code)

    password = secrets.token_urlsafe(16)
    hashed_password = hasher.hash_password(password)
    email = data['email']
    async with uow:
        user = await uow.users.get_by_email(email=email)

        if not user:
            user_data = UserCreate(email=email,
                                   username=data["name"],
                                   password=hashed_password,
                                   avatar_image=data["picture"],
                                   is_verify_email=data["email_verified"])
            user = await uow.users.add(user_data)
            await uow.commit()

        await auth.set_tokens(user)


async def oauth2_yandex_case(access_token: str, oauth2_yandex: IOauth2Provider, hasher: IHasherProvider, auth: ITokenAuth):
    uow = UsersUnitOfWork()
    if not access_token:
        raise BadRequest("No find 'access_token' in query params")

    data = await oauth2_yandex.callback(access_token)

    password = secrets.token_urlsafe(16)
    hashed_password = hasher.hash_password(password)
    email = data['default_email']

    user_data = UserCreate(email=email,
                           password=hashed_password)

    async with uow:
        user = await uow.users.get_by_email(email=email)

        if not user:
            user = await uow.users.add(user_data)
            await uow.commit()

        await auth.set_tokens(user)

