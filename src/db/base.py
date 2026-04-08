import datetime

import pytz
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from src.utils.datetimes import get_timezone_now


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer(), autoincrement=True, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=get_timezone_now)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=get_timezone_now, default=get_timezone_now)

