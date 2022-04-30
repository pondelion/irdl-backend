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

    DISABLE_AUTH: bool = False

    # DB_USERNAME: str
    # DB_PASSWORD: str
    # DB_HOST: str
    # DB_NAME: str
    # DB_PORT: int = 3306

    # @property
    # def MYSQL_DATABASE_URI(self) -> str:
    #     return f'mysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4'

    AWS_REGION_NAME: str = 'ap-northeast-1'

    AWS_IOT_COMMAND_TOPIC_NAME: str = 'irdl/command'
    AWS_IOT_LOCATION_TOPIC_NAME: str = 'irdl/logging/location'
    AWS_IOT_SENSOR_TOPIC_NAME: str = 'irdl/logging/sensor'

    S3_BUCKET_NAME: str = 'irdl-app'
    DYNAMODB_LOCATION_DATA_TABLE_NAME: str = 'irdl-location'
    DYNAMODB_SENSOR_DATA_TABLE_NAME: str = 'irdl-sensor'

    @property
    def S3_CAMERA_IMAGE_URI(self) -> str:
        return os.path.join('s3://', self.S3_BUCKET_NAME, 'camera')


settings = Settings(
    SERVER_HOST='http://127.0.0.0.1',
    DISABLE_AUTH=False
)
