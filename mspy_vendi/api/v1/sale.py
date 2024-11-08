from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.sales.schemas import SaleDetailSchema
from mspy_vendi.domain.sales.service import SaleService

router = APIRouter(prefix="/sale", default_response_class=ORJSONResponse, tags=[ApiTagEnum.SALES])


class SaleAPI(CRUDApi):
    service = SaleService
    schema = SaleDetailSchema
    current_user_mapping = {**basic_permissions}
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.SALES,)


SaleAPI(router)
