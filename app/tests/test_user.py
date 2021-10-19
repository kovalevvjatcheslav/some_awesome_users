import random
from string import ascii_letters, digits
from typing import List

from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.users import UserRequestCreate
from app.utils import encode_password, create_user
from models import User, UserType


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    return await create_user(
        db_session,
        UserRequestCreate(
            name="test_user", password="test_password", user_type=UserType.all
        ),
    )


@pytest.fixture
async def users(db_session: AsyncSession) -> List[User]:
    users_data = []
    for i in range(2):
        users_data.append(
            dict(
                name=f"test_user{i}",
                password=encode_password(f"test_password{i}"),
                user_type=random.choice([item.value for item in UserType]),
            )
        )
    db_users = [User(**data) for data in users_data]
    db_session.add_all(db_users)
    await db_session.commit()
    for db_user in db_users:
        await db_session.refresh(db_user)
    return db_users


@pytest.fixture
async def authorized_user(client: AsyncClient, user: User) -> User:
    await client.post("/login", json={"name": user.name, "password": "test_password"})
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
    async def test_get_users(
        self, client: AsyncClient, authorized_user: User, users: List[User]
    ):
        response = await client.get("/users")
        expected = sorted(
            [
                jsonable_encoder(
                    dict(
                        id=db_user.id,
                        name=db_user.name,
                        user_type=db_user.user_type,
                        created_at=db_user.created_at,
                        deleted_at=None,
                    )
                )
                for db_user in users
            ],
            key=lambda item: item["id"],
        )
        assert response.status_code == 200
        assert expected == sorted(response.json()["users"], key=lambda item: item["id"])

    @pytest.mark.asyncio
    async def test_get_users_invalid_token(
        self, client: AsyncClient, authorized_user: User
    ):
        token = client.cookies.get("token")
        client.cookies.delete("token")
        client.cookies.set("token", token[:-1])
        response = await client.get("/users")
        assert response.status_code == 403
        assert response.json() == {"detail": "Token is invalid"}

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, authorized_user: User):
        name = "".join(random.choices(ascii_letters, k=20))
        password = "".join(random.choices(ascii_letters + digits, k=10))
        response = await client.post(
            "/user", json={"name": name, "password": password, "user_type": "ro"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_user_fail_exits(
        self, client: AsyncClient, authorized_user: User
    ):
        password = "".join(random.choices(ascii_letters + digits, k=10))
        response = await client.post(
            "/user",
            json={
                "name": authorized_user.name,
                "password": password,
                "user_type": "ro",
            },
        )
        assert response.status_code == 409
        assert response.json() == {
            "detail": "The user with the current name already exists"
        }

    @pytest.mark.asyncio
    async def test_delete_user(
        self, db_session: AsyncSession, client: AsyncClient, authorized_user: User
    ):
        name = "".join(random.choices(ascii_letters, k=20))
        password = "".join(random.choices(ascii_letters + digits, k=10))
        created_user = await create_user(
            db_session,
            UserRequestCreate(name=name, password=password, user_type=UserType.ro),
        )
        response = await client.delete(f"/user/{created_user.id}")
        await db_session.refresh(created_user)
        assert response.status_code == 200
        assert created_user.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_himself_fail(
        self, db_session: AsyncSession, client: AsyncClient, authorized_user: User
    ):
        response = await client.delete(f"/user/{authorized_user.id}")
        await db_session.refresh(authorized_user)
        assert response.status_code == 409
        assert authorized_user.deleted_at is None
