import logging

from fastapi import HTTPException

from src.auth.infrastructure.providers.hasher import HasherProvider
from src.auth.presentation.dependencies import TokenAuthDep
from src.auth.presentation.dtos import UserLoginDTO
from src.users.infrastructure.db.uow import UsersUnitOfWork



async def authenticate(login_data: UserLoginDTO, auth: TokenAuthDep):
    uow = UsersUnitOfWork()
    hasher_provider = HasherProvider()

    async with uow:
        logging.info(f"Authenticate user {login_data.email}")
        user = await uow.users.get_by_email(login_data.email)

        if not user or not hasher_provider.verify_password(login_data.password, user.password):
            logging.error(f"Not valid password or email {login_data.model_dump()}")
            raise HTTPException(status_code=400,
                                detail="Not valid password or email")

        logging.info("User authenticated")
        await auth.set_tokens(user)
