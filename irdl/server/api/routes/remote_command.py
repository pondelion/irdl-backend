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
from ....utils.image import png_imgfile2base64_url


router = APIRouter(route_class=LoggingRoute)
rc = RemoteCommand()


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


@router.get('/health_check')
def health_check():
    return 'ok'
