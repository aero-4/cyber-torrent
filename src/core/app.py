from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.auth.presentation.middlewares import AuthorizationMiddleware
from src.auth.presentation.api import router as auth_api_router
from src.users.presentation.api import router as users_api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthorizationMiddleware)

app.include_router(router=auth_api_router, prefix="/auth", tags=["Auth"])
app.include_router(router=users_api_router, prefix="/users", tags=["Users"])