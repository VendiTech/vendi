from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import APIKeyHeader

from mspy_vendi.api.v1 import activity_log, geography, impression, machine, machine_impression, product, sale, user
from mspy_vendi.config import config

router_v1 = APIRouter(
    prefix="/v1",
    default_response_class=ORJSONResponse,
    dependencies=[Depends(APIKeyHeader(name=config.auth_cookie_name, auto_error=False))],
)

router_v1.include_router(activity_log.router)
router_v1.include_router(user.router)
router_v1.include_router(sale.router)
router_v1.include_router(impression.router)
router_v1.include_router(machine.router)
router_v1.include_router(product.router)
router_v1.include_router(geography.router)
router_v1.include_router(machine_impression.router)
