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
device_name = 'test_device'
rc.execute_command(device_name, params)