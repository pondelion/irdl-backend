import os
from datetime import datetime as dt

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from ...settings import settings
from ...utils.config import AWSConfig


class RemoteCameraImageModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_CAMERA_IMAGE_DATA_TABLE_NAME
        region = AWSConfig.REGION_NAME

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # local_s3_filepath = UnicodeAttribute(null=True)


class LocalCameraImageModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_CAMERA_IMAGE_DATA_TABLE_NAME
        host = f'http://localhost:{os.environ["LOCAL_DYNAMODB_PORT"]}'

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # local_s3_filepath = UnicodeAttribute(null=True)
    created_at = UTCDateTimeAttribute(default=dt.now())


CameraImageModel = None
if settings.USE_LOCAL_DYNAMODB:
    CameraImageModel = LocalCameraImageModel
else:
    CameraImageModel = RemoteCameraImageModel
