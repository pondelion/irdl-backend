import boto3

from ..utils.config import AWSConfig
from ..utils.logger import Logger


try:
    _aws_session = boto3.session.Session(
        # region_name=AWSConfig.REGION_NAME,
        aws_access_key_id=AWSConfig.LOCAL_ACCESS_KEY_ID,
        aws_secret_access_key=AWSConfig.LOCAL_SECRET_ACCESS_KEY,
    )
except Exception as e:
    Logger.e(__file__, e)
    _aws_session = boto3.session.Session()

# DYNAMO_DB_LOCAL = _aws_session.resource('dynamodb', endpoint_url=AWSConfig.LOCAL_DYNAMO_ENDPOINT_URL)
S3_LOCAL = _aws_session.resource('s3', endpoint_url=AWSConfig.LOCAL_S3_ENDPOINT_URL)
