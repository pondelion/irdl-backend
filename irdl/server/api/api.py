from fastapi import APIRouter

from .routes import (
    location,
)


api_router = APIRouter()
api_router.include_router(location.router, prefix='/location', tags=['location'])
