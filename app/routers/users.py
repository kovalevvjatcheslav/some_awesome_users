from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.dto.users import UserRequestLogin, UserRequestCreate, UserResponse
from app.utils import create_token, get_user_by_token, encode_password
from database import get_session, ALREADY_EXISTS_CODE
from models import User, UserType


router = APIRouter(tags=["users"])


@router.post("/login")
async def login(
    user: UserRequestLogin, db_session: AsyncSession = Depends(get_session)
):
    encoded_password = encode_password(user.password)
    db_user = (
        (
            await db_session.execute(
                select(User).where(
                    User.name == user.name,
                    User.password == encoded_password,
                    User.deleted_at.is_(None),
                )
            )
        )
        .scalars()
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    response = JSONResponse(content={"detail": "Ok"})
    response.set_cookie(key="token", value=create_token(db_user.id, db_user.user_type))
    return response


@router.get("/users")
async def get_users(
    db_session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(get_user_by_token),
):
    if admin_user.user_type not in (UserType.all, UserType.ro):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    # just for demonstration raw sql
    users = (
        await db_session.execute(
            "SELECT id, name, user_type, created_at FROM users u WHERE u.deleted_at IS NULL AND u.id != :user_id",
            {"user_id": admin_user.id},
        )
    ).all()
    return JSONResponse(content={"users": [jsonable_encoder(user) for user in users]})


@router.post("/user")
async def create_user(
    user: UserRequestCreate,
    db_session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(get_user_by_token),
):
    if admin_user.user_type != UserType.all:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    hashed_pass = encode_password(user.password)
    db_user = User(name=user.name, password=hashed_pass, user_type=user.user_type)
    db_session.add(db_user)
    try:
        await db_session.commit()
    except IntegrityError as e:
        if e.orig.sqlstate == ALREADY_EXISTS_CODE:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="The user with the current name already exists",
            )
    await db_session.refresh(db_user)
    result = UserResponse(**db_user.to_dict())
    return JSONResponse(content={"user": jsonable_encoder(result)})


@router.delete("/user/{user_id}")
async def create_user(
    user_id: int,
    db_session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(get_user_by_token),
):
    if admin_user.user_type != UserType.all:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="The user cannot delete himself"
        )
    deleted_user = await db_session.get(User, user_id)
    deleted_user.deleted_at = datetime.now()
    await db_session.commit()
