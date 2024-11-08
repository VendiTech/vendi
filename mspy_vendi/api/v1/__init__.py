from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import APIKeyHeader

from mspy_vendi.api.v1 import user
from mspy_vendi.config import config

router_v1 = APIRouter(
    prefix="/v1",
    default_response_class=ORJSONResponse,
    dependencies=[Depends(APIKeyHeader(name=config.auth_cookie_name, auto_error=False))],
)

router_v1.include_router(user.router)
