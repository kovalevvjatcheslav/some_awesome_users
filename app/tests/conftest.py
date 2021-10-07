from httpx import AsyncClient
import pytest

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
