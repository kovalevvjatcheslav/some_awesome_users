from hashlib import sha3_256
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import declarative_base

from settings import settings


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, index=True, unique=True)
    password = Column(String)

    @staticmethod
    def encode_password(password: str) -> str:
        # it is safer to hash the password in several iterations
        encoded_password = password
        for _ in range(settings.HASH_ITERATIONS_NUMBER):
            encoded_password = sha3_256(
                (encoded_password + settings.SECRET).encode("utf8")
            ).hexdigest()
        return encoded_password
