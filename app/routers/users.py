from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.users import User
from app.dao.users import User as DbUser
from app.database import get_session
router = APIRouter(tags=["users"])


@router.post("/login")
async def login(user: User, db_session: AsyncSession = Depends(get_session)):
    db_user = (await db_session.execute(
        select(DbUser).where(DbUser.name == user.name)
    )).first()
    encoded_password = DbUser.encode_password(user.password)
    print("*" * 100)
    print(db_user)
    print("*" * 100)
    return {"test": "test"}
