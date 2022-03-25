from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

from ...utils.config import AWSConfig


class LocationModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME
        region = 'ap-northeast-1'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    lat = NumberAttribute(null=False)
    lng = NumberAttribute(null=False)


class LocalLocationModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_LOCATION_DATA_TABLE_NAME
        host = 'http://localhost:8000'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    lat = NumberAttribute(null=False)
    lng = NumberAttribute(null=False)
