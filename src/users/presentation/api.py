from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter()


@router.get("/me")
async def get_me(request: Request):
    return request.state.user.model_dump(exclude={"password"})

