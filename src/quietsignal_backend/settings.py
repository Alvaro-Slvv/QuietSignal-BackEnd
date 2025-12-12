from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    # MySQL
    MYSQL_USER: str = Field(...)
    MYSQL_PASSWORD: str = Field(...)
    MYSQL_HOST: str = Field(...)
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_DB: str = Field(...)

    # Admin user
    ADMIN_EMAIL: str = Field(...)
    ADMIN_PASSWORD: str = Field(...)
    ADMIN_NAME: str = Field(default="Admin")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )


# global instance
settings = Settings()
