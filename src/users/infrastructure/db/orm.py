import shutil
import uuid
from pathlib import Path
from typing import List

from markupsafe import Markup
from sqladmin import ModelView
from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from starlette.datastructures import FormData
from wtforms import FileField

from src.auth.domain.entities import UserRoles
from src.db.base import Base
from src.users.domain.entities import User
from src.utils.admin import format_photo, on_model_change_photo
from src.comments.infrastructure.db.orm import CommentsOrm

class UsersOrm(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role: Mapped[UserRoles] = mapped_column(Integer(), default=UserRoles.USER, nullable=True)
    is_verify_otp: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=True)
    is_verify_email: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=True)
    avatar_image: Mapped[str] = mapped_column(String(), nullable=True)
    comments: Mapped[List["CommentsOrm"]] = relationship(back_populates="user", uselist=True)

    def to_entity(self):
        return User(
            id=self.id,
            email=self.email,
            password=self.password,
            role=self.role,
            avatar_image=self.avatar_image,
            is_verify_otp=self.is_verify_otp,
            is_verify_email=self.is_verify_email
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

    column_formatters = {
        UsersOrm.avatar_image: format_photo
    }

    column_formatters_detail = {
        UsersOrm.avatar_image: lambda m, a: format_photo(m, a, width=250)
    }

    form_overrides = dict(avatar_image=FileField)

    async def on_model_change(self, data: FormData, model, is_created, request):
        await on_model_change_photo(data)
