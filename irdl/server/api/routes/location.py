from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from .custom.logging import LoggingRoute
from ..deps import auth
from .... import schemas, models
from ....models.pynamodb import LocationModel


# router = APIRouter(prefix='/location')
router = APIRouter(route_class=LoggingRoute)


# @router.get('/{device_name}', response_model=List[schemas.LocationInDBSchema])
@router.get('/{device_name}')
def get_location(
    device_name: str,
    current_user: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    locations = LocationModel.query(device_name)
    locations = [l.attribute_values for l in locations]
    return {'locations': locations}


@router.get('/health_check')
def health_check():
    return 'ok'
