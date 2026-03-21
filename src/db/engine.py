from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///test.db")
async_session_maker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)