from sqladmin import ModelView
from starlette.datastructures import FormData
from wtforms import FileField

from src.utils.admin import on_model_change_photo


class BaseAdmin(ModelView):
    form_overrides = dict(avatar_image=FileField)

    async def on_model_change(self, data: FormData, model, is_created, request):
        await on_model_change_photo(data)
