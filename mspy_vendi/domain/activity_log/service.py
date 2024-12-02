from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.activity_log.filters import ActivityLogFilter
from mspy_vendi.domain.activity_log.manager import ActivityLogManager


class ActivityLogService(CRUDService):
    filter_class = ActivityLogFilter
    manager_class = ActivityLogManager
