from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from ..deps import auth
from .... import schemas, models
from ....services.remote_command import (
    RemoteCommandParams,
    RemoteCommand,
    CommandList,
)
from ....utils.image import png_imgfile2base64_url


router = APIRouter()
rc = RemoteCommand()


@router.post('/{device_name}')
def remote_command(
    device_name: str,
    remote_command_params: RemoteCommandParams,
    current_user: CognitoClaims = Depends(auth.get_current_user),
) -> Any:
    res = rc.execute_command(device_name, remote_command_params)
    if remote_command_params.cmd == CommandList.TAKE_PICTURE:
        res = {'image_url': png_imgfile2base64_url(res)}
    return res


@router.get('/health_check')
def health_check():
    return 'ok'
