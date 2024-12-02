from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.api import CRUDApi
from mspy_vendi.core.enums import ApiTagEnum, CRUDEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.activity_log.schemas import ActivityLogDetailSchema
from mspy_vendi.domain.activity_log.service import ActivityLogService
from mspy_vendi.domain.auth import get_current_user

router = APIRouter(prefix="/activity-log", default_response_class=ORJSONResponse, tags=[ApiTagEnum.ACTIVITY_LOG])


class ActivityLogAPI(CRUDApi):
    service = ActivityLogService
    schema = ActivityLogDetailSchema
    current_user_mapping = {
        CRUDEnum.GET: Depends(get_current_user(is_superuser=True)),
        CRUDEnum.LIST: Depends(get_current_user(is_superuser=True)),
    }
    endpoints = (CRUDEnum.LIST, CRUDEnum.GET)
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.ACTIVITY_LOG,)


ActivityLogAPI(router)
