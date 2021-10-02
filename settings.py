import os
from pydantic import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    DB_HOST: str
    DB_PORT: int
    POSTGRES_PASSWORD: str

    @property
    def PG_DSN(self):
        dsn = URL.create(
            "postgresql+asyncpg",
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.POSTGRES_DB,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
        )
        return str(dsn)


environment: str = os.getenv("ENVIRONMENT", "dev").lower()
settings = Settings(_env_file=f"config/{environment}_env")
