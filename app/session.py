from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from app.config import settings
import asyncio

dbuser = settings.SQL_USER
dbpassword = settings.SQL_PASSWORD
dbhost = settings.SQL_HOST
dbport = settings.SQL_PORT
dbname = settings.SQL_NAME
DATABASE_URL = f"postgresql+asyncpg://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}"

# 数据库引擎

engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    pool_pre_ping=True, 
    plugins=["geoalchemy2"])

# 会话工厂

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# 数据库会话。

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

