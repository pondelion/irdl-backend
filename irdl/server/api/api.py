from fastapi import APIRouter

from .routes import (
    location,
    remote_command,
    device_management,
)


api_router = APIRouter()
api_router.include_router(location.router, prefix='/location', tags=['location'])
api_router.include_router(remote_command.router, prefix='/remote_command', tags=['remote_command'])
api_router.include_router(device_management.router, prefix='/device', tags=['device'])
