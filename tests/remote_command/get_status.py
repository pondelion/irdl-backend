import os

from irdl.services.remote_command import (
    RemoteCommand,
    RemoteCommandParams,
    CommandList,
    CentralServerMessageHandler,
)

csmh = CentralServerMessageHandler()
csmh.subscribe()
rc = RemoteCommand()
params = RemoteCommandParams(
    cmd=CommandList.GET_STATUS,
)
def callback(topic, msg):
    print(f'callback called : {topic} : {msg}')
    return  topic, msg
    
csmh.add_receive_callback(
    str(params.cmd_id),
    callback=callback
)
organization_name = os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME']
device_name = f"{os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME']}1"
res = rc.execute_command(organization_name, device_name, params)
print(res)

res = csmh.wait_until_response(str(params.cmd_id))
print(f'wait_until_response res : {res}')