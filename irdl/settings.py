import os
from typing import Optional
import secrets

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8days
    # SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    # DB_USERNAME: str
    # DB_PASSWORD: str
    # DB_HOST: str
    # DB_NAME: str
    # DB_PORT: int = 3306

    # @property
    # def MYSQL_DATABASE_URI(self) -> str:
    #     return f'mysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4'


settings = Settings(
    SERVER_HOST='http://127.0.0.0.1',
)
