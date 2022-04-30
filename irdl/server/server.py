from typing import Optional

from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cloudauth.cognito import CognitoClaims

from .api import api_router
from .api.deps.auth import get_current_user
from .api.routes.custom.logging import LoggingRoute
from ..settings import settings


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
    app.dependency_overrides[get_current_user] = disable_auth_dep

app.include_router(api_router, prefix=settings.API_V1_STR)
app.router.route_class = LoggingRoute


@app.get('/')
def health_check():
    return 'healthy'


@app.get('/auth_test')
def auth_test(
    current_user: CognitoClaims = Depends(get_current_user),
):
    return {'user_info': current_user}
