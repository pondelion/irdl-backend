import os

from irdl.services.remote_command import (
    RemoteCommand,
    RemoteCommandParams,
    CommandList,
)


rc = RemoteCommand()
params = RemoteCommandParams(
    cmd=CommandList.STATR_LOGGING,
    params={
        'target': 'sensor'
    }
)
organization_name = os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME']
device_name = f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}1"
res = rc.execute_command(organization_name, device_name, params)
print(res)

