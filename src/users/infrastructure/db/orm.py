from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from src.auth.domain.entities import UserRoles
from src.db.base import Base
from src.users.domain.entities import User


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer(), autoincrement=True, primary_key=True)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role: Mapped[UserRoles] = mapped_column(Integer(), default=UserRoles.USER, nullable=True)
    is_verify_otp: Mapped[bool] = mapped_column(Boolean(), default=False)

    def to_entity(self):
        return User(
            id=self.id,
            email=self.email,
            password=self.password,
            role=self.role,
            is_verify_otp=self.is_verify_otp
        )
