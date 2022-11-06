import os

from irdl.services.device_management import DeviceManager

dm = DeviceManager()
devices = dm.get_device_list(organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'])
print(devices)
