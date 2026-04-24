from fastapi import APIRouter
from starlette.requests import Request

from templates import templates

router = APIRouter()


@router.get("/faq", include_in_schema=True)
async def faq_view(request: Request):
    return templates.TemplateResponse(name="faq.html", request=request)
