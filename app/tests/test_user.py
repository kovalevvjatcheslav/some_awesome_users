from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import encode_password
from models import User, UserType


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    hashed_pass = encode_password("test_password")
    user = User(name="test_user", password=hashed_pass, user_type=UserType.all)
    db_session.add(user)
    await db_session.commit()
    return user


class TestUser:
    @pytest.mark.asyncio
    async def test_login(self, client: AsyncClient, user: User):
        response = await client.post(
            "/login", json={"name": user.name, "password": "test_password"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Ok"}

    @pytest.mark.asyncio
    async def test_login_404(self, client: AsyncClient):
        response = await client.post(
            "/login", json={"name": "test_user", "password": "test_password"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    @pytest.mark.asyncio
    async def test_get_users(self, client: AsyncClient, user: User):
        await client.post(
            "/login", json={"name": user.name, "password": "test_password"}
        )
        response = await client.get("/users")

    @pytest.mark.asyncio
    async def test_get_users_invalid_token(self, client: AsyncClient, user: User):
        await client.post(
            "/login", json={"name": user.name, "password": "test_password"}
        )
        token = client.cookies.get("token")
        client.cookies.delete("token")
        client.cookies.set("token", token[:-1])
        response = await client.get("/users")
        assert response.status_code == 403
        assert response.json() == {"detail": "Token is invalid"}
