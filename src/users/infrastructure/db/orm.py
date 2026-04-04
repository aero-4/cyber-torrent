import shutil
import uuid
from pathlib import Path

from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from starlette.datastructures import FormData
from wtforms import FileField

from src.auth.domain.entities import UserRoles
from src.db.base import Base
from src.users.domain.entities import User
from src.utils.admin import format_image_url


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer(), autoincrement=True, primary_key=True)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role: Mapped[UserRoles] = mapped_column(Integer(), default=UserRoles.USER, nullable=True)
    is_verify_otp: Mapped[bool] = mapped_column(Boolean(), default=False)
    avatar_image: Mapped[str] = mapped_column(String(), nullable=True)

    def to_entity(self):
        return User(
            id=self.id,
            email=self.email,
            password=self.password,
            role=self.role,
            avatar_image=self.avatar_image,
            is_verify_otp=self.is_verify_otp
        )


class UsersAdmin(ModelView, model=UsersOrm):
    column_list = [
        UsersOrm.id,
        UsersOrm.email,
        UsersOrm.password,
        UsersOrm.role,
        UsersOrm.is_verify_otp,
        UsersOrm.avatar_image
    ]

    def format_photo(model, attribute):
        path = getattr(model, attribute)
        if not path:
            return "Нет фото"

        url = f"/{path}" if not path.startswith("/") else path

        return Markup(
            f'<a href="{url}" target="_blank">'
            f'<img src="{url}" width="200" style="border-top: 1px solid #eee;" />'
            f'</a>'
        )

    column_formatters = {
        UsersOrm.avatar_image: format_photo
    }

    column_formatters_detail = {
        UsersOrm.avatar_image: format_photo
    }

    form_overrides = dict(avatar_image=FileField)

    async def on_model_change(self, data: FormData, model, is_created, request):
        file = data.get("avatar_image")

        if file and hasattr(file, "filename") and file.filename:
            upload_dir = Path("static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            suffix = Path(file.filename).suffix
            filename = f"{uuid.uuid4()}{suffix}"
            full_path = upload_dir / filename

            with open(full_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Заменяем объект UploadFile в словаре data на строку пути.
            data["avatar_image"] = f"static/uploads/{filename}"

        elif not file or not hasattr(file, "filename"):
            data.pop("avatar_image", None)
