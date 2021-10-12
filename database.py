from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from settings import settings

ALREADY_EXISTS_CODE = "23505"


class PostgresqlSession:
    def __init__(self):
        self.engine = None
        self.async_session_factory = None

    def init_engine(self):
        self.engine = create_async_engine(
            settings.PG_DSN,
            echo=True,
        )
        self.async_session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def dispose_engine(self):
        await self.engine.dispose()
        self.async_session_factory = None


pg_session = PostgresqlSession()


async def get_session():
    session = pg_session.async_session_factory()
    try:
        yield session
    finally:
        await session.close()


session_context = asynccontextmanager(get_session)
