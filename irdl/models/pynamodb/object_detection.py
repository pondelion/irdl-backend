import os
from datetime import datetime as dt

from pynamodb.attributes import (ListAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model

from ...settings import settings
from ...utils.config import AWSConfig


class RemoteObjectDetectionResultModel(Model):

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
        host = f'http://localhost:{os.environ["LOCAL_DYNAMODB_PORT"]}'

    organization_device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    s3_filepath = UnicodeAttribute(null=False)
    # s3_filepath = UnicodeAttribute(range_key=True)
    # datetime = UnicodeAttribute(null=False)
    od_result = ListAttribute(null=False)
    created_at = UTCDateTimeAttribute(default=dt.now())


ObjectDetectionResultModel = None
if settings.USE_LOCAL_DYNAMODB:
    ObjectDetectionResultModel = LocalObjectDetectionResultModel
else:
    ObjectDetectionResultModel = RemoteObjectDetectionResultModel
