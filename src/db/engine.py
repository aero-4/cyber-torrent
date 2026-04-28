from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import config

engine = create_async_engine(config.database.DATABASE_URI)
async_session_maker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)