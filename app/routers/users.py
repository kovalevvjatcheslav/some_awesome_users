from fastapi import APIRouter

from app.dto.users import User

router = APIRouter(tags=["users"])


@router.post("/login")
async def login(user: User):
    print("-" * 100)
    print(user.username, user.password)
    print("-" * 100)
    return {"test": "test"}
