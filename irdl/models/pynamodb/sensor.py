from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

from ...utils.config import AWSConfig


class SensorModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_SENSOR_DATA_TABLE_NAME
        region = 'ap-northeast-1'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    max_range = NumberAttribute(null=False)
    min_delay = NumberAttribute(null=False)
    power = NumberAttribute(null=False)
    resolution = NumberAttribute(null=False)
    sensor_name = UnicodeAttribute(null=False)
    type = NumberAttribute(null=False)
    value = NumberAttribute(null=False)
    vendor = UnicodeAttribute(null=False)
    version = NumberAttribute(null=False)


class LocalSensorModel(Model):

    class Meta:
        table_name = AWSConfig.DYNAMODB_SENSOR_DATA_TABLE_NAME
        host = 'http://localhost:8000'

    device_name = UnicodeAttribute(hash_key=True)
    datetime = UnicodeAttribute(range_key=True)
    max_range = NumberAttribute(null=False)
    min_delay = NumberAttribute(null=False)
    power = NumberAttribute(null=False)
    resolution = NumberAttribute(null=False)
    sensor_name = UnicodeAttribute(null=False)
    type = NumberAttribute(null=False)
    value = NumberAttribute(null=False)
    vendor = UnicodeAttribute(null=False)
    version = NumberAttribute(null=False)