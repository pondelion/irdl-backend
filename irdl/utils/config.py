import os

import yaml

from .logger import Logger


DEFAULT_AWS_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..',
    'config/aws.yml'
)
DEFAULT_TWITTER_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..',
    'config/twitter.yml'
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


def _load_twitter_config(filepath: str = DEFAULT_TWITTER_FILEPATH):
    return yaml.safe_load(open(filepath))


def _load_datalocation_config(filepath: str = DEFAULT_DATALOCATION_FILEPATH):
    return yaml.safe_load(open(filepath))


def _load_dev_config(filepath: str = DEFAULT_DEV_FILEPATH):
    return yaml.safe_load(open(filepath))


class _AWSConfig(type):
    try:
        config = _load_aws_config()
        if 'ACCESS_KEY_ID' in config:
            os.environ['AWS_ACCESS_KEY_ID'] = config['ACCESS_KEY_ID']
            Logger.i('Config', f'Setting AWS_ACCESS_KEY_ID to {config["ACCESS_KEY_ID"][:4]}***')
        if 'SECRET_ACCESS_KEY' in config:
            os.environ['AWS_SECRET_ACCESS_KEY'] = config['SECRET_ACCESS_KEY']
            Logger.i('Config', f'Setting AWS_SECRET_ACCESS_KEY to {config["SECRET_ACCESS_KEY"][:4]}***')
        if 'REGION_NAME' in config:
            os.environ['AWS_DEFAULT_REGION'] = config['REGION_NAME']
        if 'ENDPOINT_URL' not in config:
            config['ENDPOINT_URL'] = None
        else:
            Logger.i('Config', f'Setting aws endpoint to {config["ENDPOINT_URL"]}')
    except Exception as e:
        Logger.w('Config', f'Failed to load aws config filr : {e}')
        config = {}

    def __getattr__(cls, key: str):
        try:
            return cls.config[key]
        except Exception as e:
            Logger.e('Config', f'No config value found for {key}')
            raise e


class _TwitterConfig(type):
    try:
        config = _load_twitter_config()
    except Exception as e:
        Logger.w('Config', f'Failed to load twitter config filr : {e}')
        config = {}

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


class TwitterConfig(metaclass=_TwitterConfig):
    pass


class DataLocationConfig(metaclass=_DataLocationConfig):
    pass


class DevConfig(metaclass=_DevConfig):
    pass
