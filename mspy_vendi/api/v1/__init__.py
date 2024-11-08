from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import HTTPBearer

from mspy_vendi.api.v1 import geography, impression, machine, sale, user

router_v1 = APIRouter(
    prefix="/v1",
    default_response_class=ORJSONResponse,
    dependencies=[Depends(HTTPBearer(auto_error=False))],
)

router_v1.include_router(user.router)
router_v1.include_router(sale.router)
router_v1.include_router(machine.router)
router_v1.include_router(impression.router)
router_v1.include_router(geography.router)
