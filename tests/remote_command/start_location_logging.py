from irdl.services.remote_command import (
    RemoteCommand,
    RemoteCommandParams,
    CommandList,
)


rc = RemoteCommand()
params = RemoteCommandParams(
    cmd=CommandList.STATR_LOGGING,
    params={
        'target': 'location'
    }
)
device_name = 'android_test_device1'
rc.execute_command(device_name, params)
