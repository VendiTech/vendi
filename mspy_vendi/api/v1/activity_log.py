from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi_filter import FilterDepends
from starlette.responses import StreamingResponse

from mspy_vendi.core.api import CRUDApi
from mspy_vendi.core.enums import ApiTagEnum, CRUDEnum, ExportEntityTypeEnum, ExportTypeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.activity_log.filters import ActivityLogFilter
from mspy_vendi.domain.activity_log.schemas import ActivityLogDetailSchema, ExportActivityLogDetailSchema
from mspy_vendi.domain.activity_log.service import ActivityLogService
from mspy_vendi.domain.auth import get_current_user
from mspy_vendi.domain.user.models import User

router = APIRouter(prefix="/activity-log", default_response_class=ORJSONResponse, tags=[ApiTagEnum.ACTIVITY_LOG])


@router.post("/export", response_class=StreamingResponse)
async def post__export_sales(
    export_type: ExportTypeEnum,
    query_filter: Annotated[ActivityLogFilter, FilterDepends(ActivityLogFilter)],
    activity_log_service: Annotated[ActivityLogService, Depends()],
    user: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> StreamingResponse:
    return await activity_log_service.export(
        query_filter=query_filter,
        export_type=export_type,
        entity=ExportEntityTypeEnum.ACTIVITY_LOG,
        user=user,
    )


@router.get("/export-raw-data", response_model=Page[ExportActivityLogDetailSchema])
async def get__activity_log_export_raw_data(
    query_filter: Annotated[ActivityLogFilter, FilterDepends(ActivityLogFilter)],
    activity_log_service: Annotated[ActivityLogService, Depends()],
    user: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> Page[ExportActivityLogDetailSchema]:
    return await activity_log_service.get_export_data(query_filter, user)


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
