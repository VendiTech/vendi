from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.machines.schemas import MachineDetailSchema
from mspy_vendi.domain.machines.service import MachineService

router = APIRouter(prefix="/machine", default_response_class=ORJSONResponse, tags=[ApiTagEnum.MACHINES])


class MachineAPI(CRUDApi):
    service = MachineService
    schema = MachineDetailSchema
    current_user_mapping = {**basic_permissions}
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.MACHINES,)


MachineAPI(router)
