from datetime import datetime as dt

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute

from ...utils.config import AWSConfig


class CameraImageModel(Model):

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
        host = 'http://localhost:8000'

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # local_s3_filepath = UnicodeAttribute(null=True)
    created_at = UTCDateTimeAttribute(default=dt.now())
