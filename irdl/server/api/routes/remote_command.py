from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from ..deps import auth
from .... import schemas, models
from ....services.remote_command import (
    RemoteCommandParams,
    RemoteCommand,
)


router = APIRouter()
remote_command = RemoteCommand()


@router.post('')
def remote_command(
    current_user: CognitoClaims = Depends(auth.get_current_user),
    remote_command_params: RemoteCommandParams,
) -> Any:
    device_name = current_user.username
    return 'ok'


@router.post('/')
def remote_command(
    current_user: CognitoClaims = Depends(auth.get_current_user),
    remote_command_params: RemoteCommandParams,
) -> Any:
    return 'ok'


@router.get('/health_check')
def health_check():
    return 'ok'
