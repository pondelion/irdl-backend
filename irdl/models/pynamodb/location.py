import os
from datetime import datetime as dt

from pynamodb.attributes import (NumberAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model

from ...settings import settings
from ...utils.config import AWSConfig


class RemoteLocationModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME
        region = 'ap-northeast-1'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    lat = NumberAttribute(null=False)
    lng = NumberAttribute(null=False)

    @classmethod
    def set_table_name(cls, table_name):
        cls.Meta.table_name = table_name

    @classmethod
    def set_organization_name(cls, organization_name: str):
        organization_table_name = f'{AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'
        cls.Meta.table_name = organization_table_name

    @classmethod
    def reset_table_name(cls):
        cls.Meta.table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME


class LocalLocationModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME
        host = f'http://localhost:{os.environ["LOCAL_DYNAMODB_PORT"]}'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    lat = NumberAttribute(null=False)
    lng = NumberAttribute(null=False)
    created_at = UTCDateTimeAttribute(default=dt.now())

    @classmethod
    def set_table_name(cls, table_name):
        cls.Meta.table_name = table_name

    @classmethod
    def set_organization_name(cls, organization_name: str):
        organization_table_name = f'{AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'
        cls.Meta.table_name = organization_table_name

    @classmethod
    def reset_table_name(cls):
        cls.Meta.table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME


LocationModel = None
if settings.USE_LOCAL_DYNAMODB:
    LocationModel = LocalLocationModel
else:
    LocationModel = RemoteLocationModel
