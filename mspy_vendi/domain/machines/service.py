from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.machines.filters import MachineFilter
from mspy_vendi.domain.machines.manager import MachineManager


class MachineService(CRUDService):
    manager_class = MachineManager
    filter_class = MachineFilter
