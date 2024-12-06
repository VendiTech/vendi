from mspy_vendi.core.enums import ExportEntityTypeEnum
from mspy_vendi.core.mixins.export import ExportMixin
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.activity_log.filters import ActivityLogFilter
from mspy_vendi.domain.activity_log.manager import ActivityLogManager
from mspy_vendi.domain.activity_log.schemas import ExportActivityLogDetailSchema


class ActivityLogService(CRUDService, ExportMixin):
    filter_class = ActivityLogFilter
    manager_class = ActivityLogManager

    async def get_export_data(self, query_filter: ActivityLogFilter) -> Page[ExportActivityLogDetailSchema]:
        return await self.export(query_filter, entity=ExportEntityTypeEnum.ACTIVITY_LOG, raw_result=False)
