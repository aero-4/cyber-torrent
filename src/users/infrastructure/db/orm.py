from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from src.db.base import Base


class UsersOrm(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer(), autoincrement=True, primary_key=True)
    email: Mapped[str] = mapped_column(String(), nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)