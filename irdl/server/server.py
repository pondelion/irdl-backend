import os
from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cloudauth.cognito import CognitoClaims
from pydantic import BaseModel

from ..db import init_dynamodb, init_rdb
from ..services.remote_command.subscriber import CentralServerMessageHandler
from ..settings import settings
from .api import api_router
from .api.deps.auth import cognito_current_device, cognito_current_organization
from .api.routes.custom.logging import LoggingRoute

init_rdb()
init_dynamodb()

app = FastAPI(title='irdl')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.DISABLE_AUTH:
    class DummyParams(BaseModel):
        username: str

    async def disable_auth_dep_organization(dummy_params: Optional[int] = None):
        return DummyParams(username=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'])

    async def disable_auth_dep_device(dummy_params: Optional[int] = None):
        return DummyParams(username=os.environ['AWS_COGNITO_TEST_DEVICE_USERNAME'])

    app.dependency_overrides[cognito_current_organization] = disable_auth_dep_organization
    app.dependency_overrides[cognito_current_device] = disable_auth_dep_device

app.include_router(api_router, prefix=settings.API_V1_STR)
app.router.route_class = LoggingRoute

csmh = CentralServerMessageHandler()
csmh.subscribe()


@app.get('/')
def health_check():
    return 'healthy'


@app.get('/auth_test/organization')
def auth_test_organization(
    current_organization: CognitoClaims = Depends(cognito_current_organization),
):
    return {'organization': current_organization}


@app.get('/auth_test/device')
def auth_test_device(
    current_device: CognitoClaims = Depends(cognito_current_device),
):
    return {'device': current_device}
