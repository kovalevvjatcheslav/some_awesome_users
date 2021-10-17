from base64 import standard_b64encode, standard_b64decode
import hmac
from hashlib import sha3_256
import json
from time import time
from typing import Optional, Tuple

from fastapi.security import APIKeyCookie
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from app.dto.users import UserRequestCreate
from database import session_context
from models import User
from settings import settings

ENCRYPT_ALG = "HS256"


def encode_password(password: str) -> str:
    # it is safer to hash the password in several iterations
    encoded_password = password
    for _ in range(settings.HASH_ITERATIONS_NUMBER):
        encoded_password = sha3_256(
            (encoded_password + settings.SECRET).encode("utf8")
        ).hexdigest()
    return encoded_password


def create_token(user_id: int, user_type: str) -> str:
    issued_at = int(time())
    expiration_time = issued_at + settings.TOKEN_LIFETIME
    header = json.dumps({"alg": ENCRYPT_ALG, "typ": "JWT"})
    payload = json.dumps(
        {
            "userId": user_id,
            "userType": user_type,
            "exp": expiration_time,
            "iat": issued_at,
        }
    )
    header_b64 = standard_b64encode(header.encode("utf8"))
    payload_b64 = standard_b64encode(payload.encode("utf8"))
    signature = hmac.new(
        settings.SECRET.encode("utf8"), b".".join((header_b64, payload_b64)), sha3_256
    ).hexdigest()
    return ".".join((header_b64.decode(), payload_b64.decode(), signature))


class InvalidTokenException(HTTPException):
    pass


class TokenExpiredException(HTTPException):
    pass


class UserAuth(APIKeyCookie):
    @classmethod
    def __validate_token__(cls, token: str) -> Tuple[dict, bool]:
        header_b64, payload_b64, signature = token.split(".")
        signature_to_validate = hmac.new(
            settings.SECRET.encode("utf8"),
            b".".join((header_b64.encode("utf8"), payload_b64.encode("utf8"))),
            sha3_256,
        ).hexdigest()
        payload = json.loads(standard_b64decode(payload_b64))
        return payload, signature_to_validate == signature

    async def __call__(self, request: Request) -> Optional[User]:
        token = await super().__call__(request)
        payload, valid = self.__validate_token__(token)
        if not valid:
            raise InvalidTokenException(
                status_code=HTTP_403_FORBIDDEN, detail="Token is invalid"
            )
        if payload["exp"] <= int(time()):
            raise TokenExpiredException(
                status_code=HTTP_403_FORBIDDEN, detail="Token is expired"
            )
        async with session_context() as db_session:
            db_user = (
                (
                    await db_session.execute(
                        select(User).where(
                            User.id == payload["userId"], User.deleted_at.is_(None)
                        )
                    )
                )
                .scalars()
                .first()
            )
        if not db_user:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User not found")
        return db_user


get_user_by_token = UserAuth(name="token")


async def create_user(db_session: AsyncSession, user: UserRequestCreate) -> User:
    hashed_pass = encode_password(user.password)
    db_user = User(name=user.name, password=hashed_pass, user_type=user.user_type)
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user
