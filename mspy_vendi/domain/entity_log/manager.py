from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.entity_log.models import EntityLog


class EntityLogManager(CRUDManager):
    sql_model = EntityLog
