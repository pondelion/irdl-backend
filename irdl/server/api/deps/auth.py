from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims
from irdl.utils.config import AWSConfig


get_current_user = CognitoCurrentUser(
    region=AWSConfig.REGION_NAME,
    userPoolId=AWSConfig.COGNITO_USERPOOLID,
    client_id=AWSConfig.COGNITO_CLIENT_ID,
)
