from logging import Logger
import boto3

from ...models.pynamodb import LocationModel, SensorModel
from ...settings import settings
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
        # Create cognito user for organization
        Logger.i('OrganizationManager', f'Creating cognito user for {organization_name}')
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
            ChallengeResponses={'USERNAME': organization_name, 'NEW_PASSWORD': password},
            Session=session
        )
        # Create dynamodb tables for the organization
        Logger.i('OrganizationManager', f'Creating dynamodb table for {organization_name}')
        self._create_dynamo_table(organization_name=organization_name)
        # Create iot rule for the organization
        Logger.i('OrganizationManager', f'Creating iot rule for {organization_name}')
        self._create_iot_rule(organization_name=organization_name)
        return response

    def _create_dynamo_table(self, organization_name: str):
        # location
        LocationModel.set_table_name(table_name=f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}')
        if LocationModel.exists():
            Logger.w('OrganizationManager', f'Dynamodb location table {LocationModel.Meta.table_name} already exists')
        else:
            Logger.i('OrganizationManager', f'Creating dynamodb location table {LocationModel.Meta.table_name} for organization {organization_name}..')
            LocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            Logger.i('OrganizationManager', f'Created')
        LocationModel.set_table_name(table_name=f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}')

        # sensor
        SensorModel.set_table_name(table_name=f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}-{organization_name}')
        if SensorModel.exists():
            Logger.w('OrganizationManager', f'Dynamodb sensor table {SensorModel.Meta.table_name} already exists')
        else:
            Logger.i('OrganizationManager', f'Creating dynamodb sensor table {SensorModel.Meta.table_name} for organization {organization_name}')
            SensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            Logger.i('OrganizationManager', f'Created')
        SensorModel.set_table_name(table_name=f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}')

    def _create_iot_rule(self, organization_name: str):
        dynamo_role_arn = self._create_iam_role_for_put_dynamodb(organization_name)
        # rule for transfer location data to dynamodb
        Logger.i('OrganizationManager', f'Creating location data rule for {organization_name}')
        location_table_name = f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'
        self._iot_client.create_topic_rule(
            ruleName=f'irdl-location-dynamodb-rule-{organization_name}',
            topicRulePayload={
                'sql': f"SELECT * FROM 'irdl/logging/location/{organization_name}'",
                'description': f'rule for transfer location data to dynamodb for organization {organization_name}',
                'actions': [
                    {
                        'dynamoDBv2': {
                            'roleArn': dynamo_role_arn,
                            'putItem': {
                                'tableName': location_table_name
                            }
                        },
                    }
                ],
                'ruleDisabled': False,
                'awsIotSqlVersion': '2016-03-23',
            }
        )
        # rule for transfer sensor data to dynamodb
        Logger.i('OrganizationManager', f'Creating sensor data rule for {organization_name}')
        sensor_table_name = f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}-{organization_name}'
        self._iot_client.create_topic_rule(
            ruleName=f'irdl-sensor-dynamodb-rule-{organization_name}',
            topicRulePayload={
                'sql': f"SELECT * FROM 'irdl/logging/sensor/{organization_name}'",
                'description': f'rule for transfer sensor data to dynamodb for organization {organization_name}',
                'actions': [
                    {
                        'dynamoDBv2': {
                            'roleArn': dynamo_role_arn,
                            'putItem': {
                                'tableName': sensor_table_name
                            }
                        },
                    }
                ],
                'ruleDisabled': False,
                'awsIotSqlVersion': '2016-03-23',
            }
        )

    def _create_iam_role_for_put_dynamodb(self, organization_name: str) -> str:
        role_name = f'role-irdl-iot-dynamodb-location-{organization_name}'
        location_table_name = f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'
        sensor_table_name = f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}-{organization_name}'
        Logger.i('OrganizationManager', f'Creating iam role for putting item to dynamodb')
        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "dynamodb:PutItem",
                "Resource": [
                    f"arn:aws:dynamodb:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:table/{location_table_name}",
                    f"arn:aws:dynamodb:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:table/{sensor_table_name}"
                ]
            }
        })
        create_role_response = self._iam_client.create_role(
            RoleName=role_name
            AssumeRolePolicyDocument=assume_role_policy_document
        )
        iam_arn = iams['Role']['Arn']
        return iam_arn
