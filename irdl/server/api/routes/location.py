from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from .... import models, schemas
from ....models.pynamodb import LocationModel
from ..deps import auth
from .custom.logging import LoggingRoute

# router = APIRouter(prefix='/location')
router = APIRouter(route_class=LoggingRoute)


# @router.get('/{device_name}', response_model=List[schemas.LocationInDBSchema])
@router.get('/{device_name}')
def get_location(
    device_name: str,
    current_organization: CognitoClaims = Depends(auth.cognito_current_organization),
) -> Any:
    LocationModel.set_organization_name(current_organization.username)
    locations = LocationModel.query(device_name)
    LocationModel.reset_table_name()
    locations = [l.attribute_values for l in locations]
    print(locations)
    return {'locations': locations}


@router.get('/health_check')
def health_check():
    return 'ok'
