import os

import yaml

from .logger import Logger
from ..settings import settings


DEFAULT_AWS_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..',
    'config/aws.yml'
)
DEFAULT_DATALOCATION_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..',
    'config/data_location.yml'
)
DEFAULT_DEV_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..',
    'config/dev.yml'
)


def _load_aws_config(filepath: str = DEFAULT_AWS_FILEPATH):
    return yaml.safe_load(open(filepath))


def _load_datalocation_config(filepath: str = DEFAULT_DATALOCATION_FILEPATH):
    return yaml.safe_load(open(filepath))


def _load_dev_config(filepath: str = DEFAULT_DEV_FILEPATH):
    return yaml.safe_load(open(filepath))


class _AWSConfig(type):
    try:
        config = _load_aws_config()
    except Exception as e:
        Logger.w('Config', f'Failed to load aws config filr : {e}')
        config = {}

    if 'ACCESS_KEY_ID' in config:
        os.environ['AWS_ACCESS_KEY_ID'] = config['ACCESS_KEY_ID']
        Logger.i('Config', f'Setting AWS_ACCESS_KEY_ID to {config["ACCESS_KEY_ID"][:4]}***')
    if 'SECRET_ACCESS_KEY' in config:
        os.environ['AWS_SECRET_ACCESS_KEY'] = config['SECRET_ACCESS_KEY']
        Logger.i('Config', f'Setting AWS_SECRET_ACCESS_KEY to {config["SECRET_ACCESS_KEY"][:4]}***')
    if 'REGION_NAME' in config:
        os.environ['AWS_DEFAULT_REGION'] = config['REGION_NAME']
    # if 'AWS_REGION_NAME' in os.environ:
    #     config['REGION_NAME'] = os.environ['AWS_REGION_NAME']
    # if 'AWS_COGNITO_DEVICE_USERPOOL_ID' in os.environ:
    #     config['COGNITO_DEVICE_USERPOOL_ID'] = os.environ['AWS_COGNITO_DEVICE_USERPOOL_ID']
    # if 'AWS_COGNITO_DEVICE_CLIENT_ID' in os.environ:
    #     config['COGNITO_DEVICE_CLIENT_ID'] = os.environ['AWS_COGNITO_DEVICE_CLIENT_ID']
    # if 'AWS_COGNITO_DEVICE_IDENTITY_POOL_ID' in os.environ:
    #     config['COGNITO_DEVICE_IDENTITY_POOL_ID'] = os.environ['AWS_COGNITO_DEVICE_IDENTITY_POOL_ID']
    # if 'AWS_COGNITO_ORGANIZATION_USERPOOL_ID' in os.environ:
    #     config['COGNITO_ORGANIZATION_USERPOOL_ID'] = os.environ['AWS_COGNITO_ORGANIZATION_USERPOOL_ID']
    # if 'AWS_COGNITO_ORGANIZATION_CLIENT_ID' in os.environ:
    #     config['COGNITO_ORGANIZATION_CLIENT_ID'] = os.environ['AWS_COGNITO_ORGANIZATION_CLIENT_ID']
    # if 'AWS_ACCOUNT_ID' in os.environ:
    #     config['ACCOUNT_ID'] = os.environ['AWS_ACCOUNT_ID']
    for key in os.environ:
        if not key.startswith('AWS_'):
            continue
        config[key[4:]] = os.environ[key]

    if 'MINIO_USERNAME' in os.environ:
        config['LOCAL_ACCESS_KEY_ID'] = os.environ['MINIO_USERNAME']
    if 'MINIO_PASSWORD' in os.environ:
        config['LOCAL_SECRET_ACCESS_KEY'] = os.environ['MINIO_PASSWORD']
    if 'MINIO_ENDPOINT_URL' in os.environ:
        config['LOCAL_S3_ENDPOINT_URL'] = os.environ['MINIO_ENDPOINT_URL']

    config['DYNAMODB_LOCATION_DATA_TABLE_NAME'] = settings.DYNAMODB_LOCATION_DATA_TABLE_NAME
    config['DYNAMODB_SENSOR_DATA_TABLE_NAME'] = settings.DYNAMODB_SENSOR_DATA_TABLE_NAME
    config['DYNAMODB_CAMERA_IMAGE_DATA_TABLE_NAME'] = settings.DYNAMODB_CAMERA_IMAGE_DATA_TABLE_NAME
    config['DYNAMODB_OBJECT_DETECTION_TABLE_NAME'] = settings.DYNAMODB_OBJECT_DETECTION_TABLE_NAME

    def __getattr__(cls, key: str):
        try:
            return cls.config[key]
        except Exception as e:
            Logger.e('Config', f'No config value found for {key}')
            raise e


class _DataLocationConfig(type):
    try:
        config = _load_datalocation_config()
    except Exception as e:
        Logger.w('Config', f'Failed to load data_location config filr : {e}')
        config = {}

    def __getattr__(cls, key: str):
        try:
            return cls.config[key]
        except Exception as e:
            Logger.e('Config', f'No config value found for {key}')
            raise e


class _DevConfig(type):
    try:
        config = _load_dev_config()
    except Exception as e:
        Logger.w('Config', f'Failed to load dev config filr : {e}')
        config = {}

    def __getattr__(cls, key: str):
        try:
            return cls.config[key]
        except Exception as e:
            Logger.e('Config', f'No config value found for {key}')
            raise e


class AWSConfig(metaclass=_AWSConfig):
    pass


class DataLocationConfig(metaclass=_DataLocationConfig):
    pass


class DevConfig(metaclass=_DevConfig):
    pass
