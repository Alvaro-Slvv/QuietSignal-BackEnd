from datetime import timedelta
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # MySQL pieces (from .env)
    mysql_user: str
    mysql_password: str
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+mysqlconnector://{self.mysql_user}:"
            f"{self.mysql_password}@{self.mysql_host}:"
            f"{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
