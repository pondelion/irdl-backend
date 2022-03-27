from fastapi import FastAPI
from irdl.server.api import api_router
from irdl.settings import settings


app = FastAPI(title='irdl')

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get('/')
def health_check():
    return 'healthy'
