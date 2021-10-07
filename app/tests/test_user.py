from fastapi.testclient import TestClient

import pytest

from app.main import app

# client = TestClient(app)


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post(
        "/login", json={"username": "test_user", "password": "test_password"}
    )
    print(response.status_code)
    print(response.json())
