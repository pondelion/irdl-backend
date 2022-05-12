from datetime import datetime as dt

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute, MapAttribute, UTCDateTimeAttribute

from ...utils.config import AWSConfig
from ...settings import settings


class ObjectDetectionResultModel(Model):

    class Meta:
        table_name = settings.DYNAMODB_OBJECT_DETECTION_TABLE_NAME
        region = AWSConfig.REGION_NAME

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # s3_filepath = UnicodeAttribute(range_key=True)
    # datetime = UnicodeAttribute(null=False)
    od_result = ListAttribute(null=False)


class LocalObjectDetectionResultModel(Model):

    class Meta:
        table_name = settings.DYNAMODB_OBJECT_DETECTION_TABLE_NAME
        host = 'http://localhost:8000'

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # s3_filepath = UnicodeAttribute(range_key=True)
    # datetime = UnicodeAttribute(null=False)
    od_result = ListAttribute(null=False)
    created_at = UTCDateTimeAttribute(default=dt.now())
