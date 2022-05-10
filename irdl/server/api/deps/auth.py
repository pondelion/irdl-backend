from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser
from irdl.utils.config import AWSConfig


cognito_current_device = CognitoCurrentUser(
    region=AWSConfig.REGION_NAME,
    userPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
    client_id=AWSConfig.COGNITO_DEVICE_CLIENT_ID,
)
cognito_current_organization = CognitoCurrentUser(
    region=AWSConfig.REGION_NAME,
    userPoolId=AWSConfig.COGNITO_ORGANIZATION_USERPOOL_ID,
    client_id=AWSConfig.COGNITO_ORGANIZATION_CLIENT_ID,
)
