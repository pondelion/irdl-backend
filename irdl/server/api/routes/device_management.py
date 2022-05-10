from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from .custom.logging import LoggingRoute
from ..deps import auth
from .... import schemas, models
from ....services.device_management import DeviceManager
from ....utils.image import png_imgfile2base64_url


router = APIRouter(route_class=LoggingRoute)
dm = DeviceManager()


@router.get('')
def get_device_list(
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Dict[str, List[schemas.DeviceSchema]]:
    # devices = dm.get_device_list(organization_name=current_organization.username)
    devices = dm.get_device_list(organization_name='organization1')
    print(devices)
    return {'devices': devices}


@router.get('/health_check')
def health_check():
    return 'ok'
