from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models import UserType


class UserBase(BaseModel):
    name: str


class PasswordMixin(BaseModel):
    password: str


class UserTypeMixin(BaseModel):
    user_type: UserType


class UserRequestLogin(PasswordMixin, UserBase):
    pass


class UserRequestCreate(PasswordMixin, UserTypeMixin, UserBase):
    pass


class UserResponse(UserTypeMixin, UserBase):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime]
