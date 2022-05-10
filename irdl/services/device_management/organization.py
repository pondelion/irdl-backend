import json
from typing import Dict

import boto3
from tenacity import retry, wait_exponential

from ...models.pynamodb import LocationModel, SensorModel
from ...settings import settings
from ...utils.config import AWSConfig
from ...utils import Logger


class OrganizationManager:

    def __init__(self):
        self._idp_client = boto3.client('cognito-idp')
        self._iot_client = boto3.client('iot')
        self._iam_client = boto3.client('iam')

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
        self._create_iot_rule(organization_name=organization_name)
        return response

    def _create_dynamo_table(self, organization_name: str):
        # location
        LocationModel.set_table_name(table_name=self._get_dynamo_location_table_name(organization_name))
        if LocationModel.exists():
            Logger.w('OrganizationManager', f'Dynamodb location table {LocationModel.Meta.table_name} already exists')
        else:
            Logger.i('OrganizationManager', f'Creating dynamodb location table {LocationModel.Meta.table_name} for organization {organization_name}..')
            LocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            Logger.i('OrganizationManager', f'Created')
        LocationModel.set_table_name(table_name=f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}')

        # sensor
        SensorModel.set_table_name(table_name=self._get_dynamo_sensor_table_name(organization_name))
        if SensorModel.exists():
            Logger.w('OrganizationManager', f'Dynamodb sensor table {SensorModel.Meta.table_name} already exists')
        else:
            Logger.i('OrganizationManager', f'Creating dynamodb sensor table {SensorModel.Meta.table_name} for organization {organization_name}')
            SensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            Logger.i('OrganizationManager', f'Created')
        SensorModel.set_table_name(table_name=f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}')

    def _create_iot_rule(self, organization_name: str):
        dynamo_role_arn = self._create_iam_role_for_put_dynamodb(organization_name)
        Logger.i('OrganizationManager', f'Created : {dynamo_role_arn}')
        # rule for transfer location data to dynamodb
        Logger.i('OrganizationManager', f'Creating location data rule for {organization_name}')
        location_table_name = f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'
        self._create_topic_rule(
            ruleName=self._get_location_iot_topic_rule_name(organization_name),
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
        self._create_topic_rule(
            ruleName=self._get_sensor_iot_topic_rule_name(organization_name),
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
        # Create role
        role_name = self._get_iot_role_name(organization_name)
        location_table_name = self._get_dynamo_location_table_name(organization_name)
        sensor_table_name = self._get_dynamo_sensor_table_name(organization_name)
        Logger.i('OrganizationManager', f'Creating iam role for putting item to dynamodb')
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "iot.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        try:
            create_role_res = self._iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
            )
        except Exception as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                raise e
            else:
                raise e
        role_arn = create_role_res['Role']['Arn']

        # Create policy
        Logger.i('OrganizationManager', f'Creating policy for putting item to dynamodb')
        policy_name = self._get_iot_policy_name(organization_name)
        policy_document = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "dynamodb:PutItem",
                "Resource": [
                    f"arn:aws:dynamodb:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:table/{location_table_name}",
                    f"arn:aws:dynamodb:ap-northeast-1:{AWSConfig.ACCOUNT_ID}:table/{sensor_table_name}"
                ]
            }
        }
        try:
            policy_res = self._iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            policy_arn = policy_res['Policy']['Arn']
        except Exception as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                policy_arn = 'arn:aws:iam::' + AWSConfig.ACCOUNT_ID + ':policy/' + policy_name
            else:
                Logger.e('OrganizationManager', f'Error occured when creating policy, deleting role {role_name}')
                self._iam_client.delete_role(RoleName=role_name)
                raise e

        # Attach policy to role
        Logger.i('OrganizationManager', f'Attaching policy to role')
        try:
            policy_attach_res = self._iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when attaching policy to role, deleting role {role_name}')
            self._iam_client.delete_role(RoleName=role_name)
            raise e
        return role_arn

    @retry(wait=wait_exponential(multiplier=3, min=3, max=3*60))
    def _create_topic_rule(self, ruleName: str, topicRulePayload: Dict) -> Dict:
        Logger.i('OrganizationManager', 'Trying..')
        res = self._iot_client.create_topic_rule(
            ruleName=ruleName,
            topicRulePayload=topicRulePayload
        )
        Logger.i('OrganizationManager', f'Created : {res}')
        return res

    def creanup_all_resources(self, organization_name: str):
        # Clean up iot topic rule
        location_rule_name = self._get_location_iot_topic_rule_name(organization_name)
        try:
            Logger.i('OrganizationManager', f'Deleting iot location topic rule : {location_rule_name}')
            self._iot_client.delete_topic_rule(
                ruleName=location_rule_name
            )
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting location topic rule : {e}')
        sensor_rule_name = self._get_sensor_iot_topic_rule_name(organization_name)
        try:
            Logger.i('OrganizationManager', f'Deleting iot sensor topic rule : {sensor_rule_name}')
            self._iot_client.delete_topic_rule(
                ruleName=sensor_rule_name
            )
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting sensor topic rule : {e}')
        # Clean up iam policy
        policy_name = self._get_iot_policy_name(organization_name)
        policy_arn = 'arn:aws:iam::' + AWSConfig.ACCOUNT_ID + ':policy/' + policy_name
        role_name = self._get_iot_role_name(organization_name)
        try:
            Logger.i('OrganizationManager', f'Detaching policy from role : {policy_name}')
            policy_detach_res = self._iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when detaching policy : {e}')
        try:
            Logger.i('OrganizationManager', f'Deleting policy : {policy_name}')
            policy_res = self._iam_client.delete_policy(PolicyArn=policy_arn)
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting policy : {e}')
        # Clean up iam role
        try:
            Logger.i('OrganizationManager', f'Deleting role : {role_name}')
            role_res = self._iam_client.delete_role(RoleName=role_name)
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting role : {e}')
        # Clean up dynamodb table
        location_table_name = self._get_dynamo_location_table_name(organization_name)
        try:
            Logger.i('OrganizationManager', f'Deleting dynamodb location table : {location_table_name}')
            LocationModel.set_table_name(table_name=location_table_name)
            LocationModel.delete_table()
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting dynamo location table : {e}')
        finally:
            LocationModel.set_table_name(table_name=f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}')
        sensor_table_name = self._get_dynamo_sensor_table_name(organization_name)
        try:
            Logger.i('OrganizationManager', f'Deleting dynamodb sensor table : {sensor_table_name}')
            SensorModel.set_table_name(table_name=sensor_table_name)
            SensorModel.delete_table()
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting dynamo sensor table : {e}')
        finally:
            SensorModel.set_table_name(table_name=f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}')
        # Clean up cognito user
        try:
            Logger.i('OrganizationManager', f'Deleting cognito user : {organization_name}')
            self._idp_client.admin_delete_user(
                UserPoolId=AWSConfig.COGNITO_ORGANIZATION_USERPOOL_ID,
                Username=organization_name
            )
            Logger.i('OrganizationManager', 'Done')
        except Exception as e:
            Logger.e('OrganizationManager', f'Error occured when deleting cognito user : {e}')

    def _get_location_iot_topic_rule_name(self, organization_name: str) -> str:
        return f'irdl-location-dynamodb-rule-{organization_name}'.replace('-', '_')

    def _get_sensor_iot_topic_rule_name(self, organization_name: str) -> str:
        return f'irdl-sensor-dynamodb-rule-{organization_name}'.replace('-', '_')

    def _get_iot_policy_name(self, organization_name: str) -> str:
        return f'policy-irdl-iot-dynamodb-{organization_name}'

    def _get_iot_role_name(self, organization_name: str) -> str:
        return f'role-irdl-iot-dynamodb-{organization_name}'

    def _get_dynamo_location_table_name(self, organization_name: str) -> str:
        return f'{settings.DYNAMODB_LOCATION_DATA_TABLE_NAME}-{organization_name}'

    def _get_dynamo_sensor_table_name(self, organization_name: str) -> str:
        return f'{settings.DYNAMODB_SENSOR_DATA_TABLE_NAME}-{organization_name}'
