from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.dto.users import User
from app.utils import create_token, get_user_by_token, encode_password
from database import get_session
from models import User as DbUser, UserType


router = APIRouter(tags=["users"])


@router.post("/login")
async def login(user: User, db_session: AsyncSession = Depends(get_session)):
    encoded_password = encode_password(user.password)
    db_user = (
        (
            await db_session.execute(
                select(DbUser).where(
                    DbUser.name == user.name,
                    DbUser.password == encoded_password,
                    DbUser.deleted_at.is_(None),
                )
            )
        )
        .scalars()
        .first()
    )
    if db_user:
        response = JSONResponse(content={"detail": "Ok"})
        response.set_cookie(
            key="token", value=create_token(db_user.id, db_user.user_type)
        )
    else:
        response = JSONResponse(status_code=404, content={"detail": "User not found"})
    return response


@router.get("/users")
async def get_users(
    db_session: AsyncSession = Depends(get_session),
    user: DbUser = Depends(get_user_by_token),
):
    if user.user_type not in (UserType.all, UserType.ro):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User not found")
    return {"test": "test"}
