from sqlalchemy import Integer, String, Enum
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

    def to_entity(self):
        return User(
            id=self.id,
            email=self.email,
            password=self.password,
            role=self.role
        )
