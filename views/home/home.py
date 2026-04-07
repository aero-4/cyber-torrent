from fastapi import APIRouter
from starlette.requests import Request

from templates import templates

router = APIRouter(tags=["Home views"])


@router.get("/", include_in_schema=True)
async def home_view(request: Request):
    return templates.TemplateResponse(name="home.html", request=request)
