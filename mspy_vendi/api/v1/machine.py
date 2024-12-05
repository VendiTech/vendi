from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi_filter import FilterDepends

from mspy_vendi.core.api import CRUDApi, admin_permissions, basic_endpoints
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_current_user
from mspy_vendi.domain.machines.filters import MachineFilter
from mspy_vendi.domain.machines.schemas import MachineCreateSchema, MachineDetailSchema, MachinesCountGeographySchema
from mspy_vendi.domain.machines.service import MachineService
from mspy_vendi.domain.user.models import User

router = APIRouter(prefix="/machine", default_response_class=ORJSONResponse, tags=[ApiTagEnum.MACHINES])


@router.get("/count-per-geography", response_model=Page[MachinesCountGeographySchema])
async def get__machines_count_per_geography(
    query_filter: Annotated[MachineFilter, FilterDepends(MachineFilter)],
    machine_service: Annotated[MachineService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[MachinesCountGeographySchema]:
    return await machine_service.get_machines_count_per_geography(query_filter, user)


class MachineAPI(CRUDApi):
    service = MachineService
    schema = MachineDetailSchema
    create_schema = MachineCreateSchema
    current_user_mapping = admin_permissions
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.MACHINES,)


MachineAPI(router)
