from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi_cloudauth.cognito import CognitoClaims

from ..deps import auth
from .... import schemas, models


# router = APIRouter(prefix='/location')
router = APIRouter()


@router.get('', response_model=List[schemas.LocationInDBSchema])
def get_location(
    skip: int = 0,
    limit: int = 100,
    current_user: CognitoClaims = Depends(auth.get_current_user),
) -> Any:
    return 'ok'


@router.get('/', response_model=List[schemas.LocationInDBSchema])
def get_location(
    skip: int = 0,
    limit: int = 100,
    current_user: CognitoClaims = Depends(auth.get_current_user),
) -> Any:
    return 'ok'


@router.get('/health_check')
def health_check():
    return 'ok'
