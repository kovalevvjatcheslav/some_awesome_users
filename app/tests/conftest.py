from httpx import AsyncClient
import pytest

from app.database import pg_session, Base
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(autouse=True)
async def init_db():
    pg_session.init_engine()
    async with pg_session.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with pg_session.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await pg_session.dispose_engine()
