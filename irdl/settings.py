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

    REMOTE_RDB_HOST: Optional[str] = None
    REMOTE_RDB_PORT: Optional[int] = 3306
    REMOTE_RDB_NAME: Optional[str] = None
    REMOTE_RDB_USERNAME: Optional[str] = None
    REMOTE_RDB_PASSWORD: Optional[str] = None

    LOCAL_RDB_HOST: Optional[str] = '127.0.0.1'
    LOCAL_RDB_PORT: Optional[int] = 3306
    LOCAL_RDB_NAME: Optional[str] = None
    LOCAL_RDB_USERNAME: Optional[str] = None
    LOCAL_RDB_PASSWORD: Optional[str] = None

    @property
    def REMOTE_MYSQL_DATABASE_URI(self) -> str:
        if self.REMOTE_RDB_HOST is None:
            raise ValueError('Remote rdb host is not set.')
        return f'mysql://{self.REMOTE_RDB_USERNAME}:{self.REMOTE_RDB_PASSWORD}@{self.REMOTE_RDB_HOST}:{self.REMOTE_RDB_PORT}/{self.REMOTE_RDB_NAME}?charset=utf8mb4'

    @property
    def LOCAL_MYSQL_DATABASE_URI(self) -> str:
        if self.self.LOCAL_RDB_NAME is None:
            raise ValueError('Local rdb name is not set.')
        return f'mysql://{self.LOCAL_RDB_USERNAME}:{self.LOCAL_RDB_PASSWORD}@{self.LOCAL_RDB_HOST}:{self.LOCAL_RDB_PORT}/{self.LOCAL_RDB_NAME}?charset=utf8mb4'

    AWS_REGION_NAME: str = 'ap-northeast-1'

    AWS_IOT_COMMAND_TOPIC_NAME: str = 'irdl/command'
    AWS_IOT_LOCATION_TOPIC_NAME: str = 'irdl/logging/location'
    AWS_IOT_SENSOR_TOPIC_NAME: str = 'irdl/logging/sensor'
    AWS_IOT_CENTRAL_SERVER_TOPIC_NAME: str = 'irdl/central_server'

    S3_BUCKET_NAME: str = 'irdl-app'
    DYNAMODB_LOCATION_DATA_TABLE_NAME: str = 'irdl-location'
    DYNAMODB_SENSOR_DATA_TABLE_NAME: str = 'irdl-sensor'
    DYNAMODB_OBJECT_DETECTION_TABLE_NAME: str = 'irld-object-detection'
    DYNAMODB_CAMERA_IMAGE_DATA_TABLE_NAME: str = 'irld-camera-image'

    @property
    def S3_CAMERA_IMAGE_URI(self) -> str:
        return os.path.join('s3://', self.S3_BUCKET_NAME, 'camera')


settings = Settings(
    SERVER_HOST='http://127.0.0.0.1',
    DISABLE_AUTH=False,
    REMOTE_RDB_HOST='a',
    REMOTE_RDB_NAME='irdl',
    REMOTE_RDB_USERNAME=os.environ['REMOTE_RDB_USERNAME'],
    REMOTE_RDB_PASSWORD=os.environ['REMOTE_RDB_PASSWORD'],
    LOCAL_RDB_PORT=3307,
    LOCAL_RDB_NAME='irdl',
    LOCAL_RDB_USERNAME=os.environ['LOCAL_RDB_USERNAME'],
    LOCAL_RDB_PASSWORD=os.environ['LOCAL_RDB_PASSWORD'],
)
