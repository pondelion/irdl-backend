import os
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi_cloudauth.cognito import CognitoClaims

from ....services.remote_command import (CommandList, RemoteCommand,
                                         RemoteCommandParams)
from ....services.remote_command.subscriber import CentralServerMessageHandler
from ....utils.image import png_imgfile2base64_url
from ..deps import auth
from .custom.logging import LoggingRoute

router = APIRouter(route_class=LoggingRoute)
rc = RemoteCommand()
csmh = CentralServerMessageHandler()


@router.get('/health_check')
def health_check():
    return 'ok'


@router.post('/{device_name}')
def remote_command(
    device_name: str,
    remote_command_params: RemoteCommandParams,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    if remote_command_params.cmd == CommandList.TAKE_PICTURE:
        img_filepath = res
        res = {'image_url': png_imgfile2base64_url(img_filepath) if img_filepath else None}
        if img_filepath is not None:
            try:
                os.remove(img_filepath)
            except Exception as e:
                print(e)
    return res


@router.get('/{device_name}/status')
def remote_command_status(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
    timeout_sec: float = 6.0,
) -> Any:
    organization_name = current_organization.username
    rc = RemoteCommand()
    params = RemoteCommandParams(
        cmd=CommandList.GET_STATUS,
    )

    def callback(topic, msg):
        print(f'callback called : {topic} : {msg}')

    csmh.add_receive_callback(
        str(params.cmd_id),
        callback=callback
    )
    res = rc.execute_command(organization_name, device_name, params)
    print(res)
    res = csmh.wait_until_response(str(params.cmd_id), timeout_sec=timeout_sec)
    return {'status': res.get('status', None) if res is not None else None}


@router.post('/{device_name}/start_logging/location')
def remote_command_start_logging_location(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.STATR_LOGGING,
        params={'target': 'location'}
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/stop_logging/location')
def remote_command_stop_logging_location(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.STOP_LOGGING,
        params={'target': 'location'}
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/start_logging/sensor')
def remote_command_start_logging_sensor(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.STATR_LOGGING,
        params={'target': 'sensor'}
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/stop_logging/sensor')
def remote_command_stop_logging_sensor(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.STOP_LOGGING,
        params={'target': 'sensor'}
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/picture')
def remote_command_take_picture(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
    successive: bool = False,
    interval_sec: float = Query(default=0.4, ge=0.3),
) -> Any:
    organization_name = current_organization.username
    if successive:
        remote_command_params = RemoteCommandParams(
            cmd=CommandList.TAKE_SUCCESSIVE_PICTURE,
            params={
                'interval_sec': interval_sec,
            },
        )
    else:
        remote_command_params = RemoteCommandParams(
            cmd=CommandList.TAKE_PICTURE,
        )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    res = {'image_url': png_imgfile2base64_url(res)} if res is not None else None
    return res


@router.post('/{device_name}/beep')
def remote_command_beep(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.BEEP,
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/start_streaming')
def remote_command_start_streaming(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.START_STREAMING,
        params={
            'url': 'TODO',
        }
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res


@router.post('/{device_name}/stop_streaming')
def remote_command_stop_streaming(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    organization_name = current_organization.username
    remote_command_params = RemoteCommandParams(
        cmd=CommandList.STOP_STREAMING,
    )
    res = rc.execute_command(organization_name, device_name, remote_command_params)
    return res
