from typing import Optional

from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cloudauth.cognito import CognitoClaims

from .api import api_router
from .api.deps.auth import cognito_current_organization, cognito_current_device
from .api.routes.custom.logging import LoggingRoute
from ..settings import settings
from ..db import init_rdb, init_dynamodb
from ..services.remote_command.subscriber import CentralServerMessageHandler


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
    async def disable_auth_dep(dummy_params: Optional[int] = None):
        return dummy_params
    app.dependency_overrides[cognito_current_organization] = disable_auth_dep
    app.dependency_overrides[cognito_current_device] = disable_auth_dep

app.include_router(api_router, prefix=settings.API_V1_STR)
app.router.route_class = LoggingRoute

csmh = CentralServerMessageHandler()
csmh.subscribe()


@app.get('/')
def health_check():
    return 'healthy'


@app.get('/auth_test/organization')
def auth_test(
    current_organization: CognitoClaims = Depends(cognito_current_organization),
):
    return {'organization': current_organization}


@app.get('/auth_test/device')
def auth_test(
    current_device: CognitoClaims = Depends(cognito_current_device),
):
    return {'device': current_device}
