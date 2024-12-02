from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.activity_log.models import ActivityLog


class ActivityLogManager(CRUDManager):
    sql_model = ActivityLog
