import re
from typing import List

import boto3

from ...schemas import DeviceSchema
from ...utils.config import AWSConfig


class DeviceManager:

    def __init__(self):
        self._idp_client = boto3.client('cognito-idp')
        self._identity_client = boto3.client('cognito-identity')
        self._iot_client = boto3.client('iot')

    def create_device_and_policy(
        self,
        organization_name: str,
        device_name: str,
        password: str,
    ):
        self._create_device(
            organization_name=organization_name,
            device_name=device_name,
            password=password
        )
        policy_name = self._create_policy(
            organization_name=organization_name,
            device_name=device_name,
        )
        identity_id = self._get_identity_id(
            organization_name=organization_name,
            device_name=device_name,
            password=password,
        )
        self._attach_policy(
            policy_name=policy_name,
            identity_id=identity_id,
        )
        self._attach_thing_principal(
            thing_name=self._get_user_name(organization_name, device_name),
            identity_id=identity_id,
        )

    def get_device_list(self, organization_name: str) -> List[DeviceSchema]:
        response = self._idp_client.list_users(
            UserPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
        )
        users = response['Users']
        organization_users = [
            usr for usr in users if any([
                attr['Name']=='custom:organization' and attr['Value']==organization_name for attr in usr['Attributes']
            ])
        ]
        organizationz = [
            [
                attr['Value'] for attr in user['Attributes'] if attr['Name']=='custom:organization'
            ][0]
            for user in organization_users
        ]
        device_dicts = [
            {
                'device_name': user['Username'],
                'organization': organization,
                'created_at': user['UserCreateDate'],
                'updated_at': user['UserLastModifiedDate'],
                'enabled': bool(user['Enabled'])
            }
            for user, organization in zip(organization_users, organizationz)
        ]
        device_objs = [DeviceSchema.parse_obj(d) for d in device_dicts]
        return device_objs

    def _create_device(
        self,
        organization_name: str,
        device_name: str,
        password: str,
    ):
        user_name = self._get_user_name(organization_name, device_name)
        # create cognito user
        self._idp_client.admin_create_user(
            UserPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
            Username=user_name,
            TemporaryPassword=password,
            UserAttributes=[{'Name': 'custom:organization', 'Value': organization_name}],
            MessageAction='SUPPRESS'
        )

        response = self._idp_client.admin_initiate_auth(
            UserPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
            ClientId=AWSConfig.COGNITO_DEVICE_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={'USERNAME': user_name, 'PASSWORD': password},
        )
        session = response['Session']

        response = self._idp_client.admin_respond_to_auth_challenge(
            UserPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
            ClientId=AWSConfig.COGNITO_DEVICE_CLIENT_ID,
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={'USERNAME': user_name, 'NEW_PASSWORD': password},
            Session=session
        )

        # create iot thing
        thing_name = user_name
        response = self._iot_client.create_thing(
            thingName=thing_name,
            # thingTypeName='string',
            attributePayload={
                'attributes': {
                    'organization_name': 'organization_name'
                },
            },
        )

        return response

    def _create_policy(
        self,
        organization_name: str,
        device_name: str,
    ):
        policy_document = f'''
        {{
        "Version": "2012-10-17",
        "Statement": [
            {{
            "Effect": "Allow",
            "Action": [
                "iot:Connect"
            ],
            "Resource": [
                "*"
            ]
            }},
            {{
            "Effect": "Allow",
            "Action": [
                "iot:Subscribe"
            ],
            "Resource": [
                "arn:aws:iot:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:topicfilter/irdl/command/{organization_name}/{device_name}"
            ]
            }},
            {{
            "Effect": "Allow",
            "Action": [
                "iot:Receive"
            ],
            "Resource": [
                "arn:aws:iot:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:topic/irdl/command/{organization_name}/{device_name}"
            ]
            }},
            {{
            "Effect": "Allow",
            "Action": [
                "iot:Publish"
            ],
            "Resource": [
                "arn:aws:iot:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:topic/irdl/logging/location/{organization_name}",
                "arn:aws:iot:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:topic/irdl/logging/sensor/{organization_name}",
                "arn:aws:iot:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:topic/irdl/central_server"
            ]
            }}
        ]
        }}
        '''
        pattern = re.compile(r'[\s\r\n]+')
        policy_document = re.sub(pattern, '', policy_document)

        policy_name = f'policy_irdl_{organization_name}_{device_name}'
        response = self._iot_client.create_policy(
            policyName=policy_name,
            policyDocument=policy_document,
        )
        return policy_name

    def _attach_policy(self, policy_name: str, identity_id: str):
        response = self._iot_client.attach_policy(
            policyName=policy_name,
            target=identity_id
        )
        return response

    def _attach_thing_principal(self, thing_name: str, identity_id: str):
        response = self._iot_client.attach_thing_principal(
            thingName=thing_name,
            principal=identity_id,
        )
        return response

    def _get_identity_id(self, organization_name: str, device_name: str, password: str) -> str:
        user_name = f'{organization_name}_{device_name}'
        auth_result = self._idp_client.admin_initiate_auth(
            UserPoolId=AWSConfig.COGNITO_DEVICE_USERPOOL_ID,
            ClientId=AWSConfig.COGNITO_DEVICE_CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters = {
                "USERNAME": user_name,
                "PASSWORD": password,
            }
        )
        id_token = auth_result["AuthenticationResult"]["IdToken"]
        response = self._identity_client.get_id(
            IdentityPoolId=AWSConfig.COGNITO_DEVICE_IDENTITY_POOL_ID,
            Logins={
                f'cognito-idp.ap-northeast-1.amazonaws.com/{AWSConfig.COGNITO_DEVICE_USERPOOL_ID}': id_token
            }
        )
        return response['IdentityId']

    def _get_user_name(self, organization_name: str, device_name: str) -> str:
        user_name = f'{organization_name}_{device_name}'
