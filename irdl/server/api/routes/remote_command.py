from typing import Any
import os

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from .custom.logging import LoggingRoute
from ..deps import auth
from .... import schemas, models
from ....services.remote_command import (
    RemoteCommandParams,
    RemoteCommand,
    CommandList,
)
from ....services.remote_command.subscriber import CentralServerMessageHandler
from ....utils.image import png_imgfile2base64_url


router = APIRouter(route_class=LoggingRoute)
rc = RemoteCommand()
csmh = CentralServerMessageHandler()


@router.post('/{device_name}')
def remote_command(
    device_name: str,
    remote_command_params: RemoteCommandParams,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    if remote_command_params.cmd == CommandList.TAKE_PICTURE:
        res = {'image_url': png_imgfile2base64_url(res)}
        try:
            os.remove(res)
        except Exception as e:
            print(e)
    return res


@router.get('/status/{device_name}')
def remote_command(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
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
    res = rc.execute_command(organization_name, device_name, params)
    print(res)
    topic, msg = csmh.wait_until_response(str(params.cmd_id))
    return {'status': msg}


@router.get('/health_check')
def health_check():
    return 'ok'
