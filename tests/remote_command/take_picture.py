import os

from irdl.services.remote_command import (
    RemoteCommand,
    RemoteCommandParams,
    CommandList,
)


rc = RemoteCommand()
params = RemoteCommandParams(
    cmd=CommandList.TAKE_PICTURE,
    params={
        # 's3_filepath': 's3://***'
    }
)
organization_name = os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME']
device_name = f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}1"
img_filepath = rc.execute_command(organization_name, device_name, params)
print(img_filepath)
