from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.machines.models import Machine


class MachineManager(CRUDManager):
    sql_model = Machine
