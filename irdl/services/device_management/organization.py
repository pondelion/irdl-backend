import boto3

from ...utils.config import AWSConfig


class OrganizationManager:

    def __init__(self):
        self._idp_client = boto3.client('cognito-idp')
        self._iot_client = boto3.client('iot')

    def create_organization(
        self,
        organization_name: str,
        mail_address: str,
        password: str,
    ):
        self._idp_client.admin_create_user(
            UserPoolId=AWSConfig.COGNITO_ORGANIZATION_USERPOOL_ID,
            Username=organization_name,
            TemporaryPassword=password,
            UserAttributes=[{'Name': 'email', 'Value': mail_address}],
            MessageAction='SUPPRESS'
        )
        response = self._idp_client.admin_initiate_auth(
            UserPoolId=AWSConfig.COGNITO_ORGANIZATION_USERPOOL_ID,
            ClientId=AWSConfig.COGNITO_ORGANIZATION_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={'USERNAME': organization_name, 'PASSWORD': password},
        )
        session = response['Session']

        response = self._idp_client.admin_respond_to_auth_challenge(
            UserPoolId=AWSConfig.COGNITO_ORGANIZATION_USERPOOL_ID,
            ClientId=AWSConfig.COGNITO_ORGANIZATION_CLIENT_ID,
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={'USERNAME': username, 'NEW_PASSWORD': password},
            Session=session
        )
        return response
