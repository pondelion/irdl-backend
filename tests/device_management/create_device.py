import os
from irdl.services.device_management import DeviceManager


dm = DeviceManager()

#
res = dm._create_device(
    organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'],
    device_name=f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}1",
    password=os.environ['AWS_COGNITO_TEST_DEVICE_PASSWORD'],
)
print(res)
res = dm._create_device(
    organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'],
    device_name=f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}2",
    password=os.environ['AWS_COGNITO_TEST_DEVICE_PASSWORD'],
)
print(res)
res = dm._create_device(
    organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'],
    device_name=f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}3",
    password=os.environ['AWS_COGNITO_TEST_DEVICE_PASSWORD'],
)
print(res)
