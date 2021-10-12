from enum import Enum

from sqlalchemy import Column, BigInteger, String, Enum as EnumType, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.functions import now

Base = declarative_base()


class UserType(str, Enum):
    all = "all"
    ro = "ro"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(EnumType(UserType), nullable=False)
    created_at = Column(DateTime, server_default=now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
