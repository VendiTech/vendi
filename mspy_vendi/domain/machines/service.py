from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.machines.filters import MachineFilter
from mspy_vendi.domain.machines.manager import MachineManager
from mspy_vendi.domain.machines.schemas import MachinesCountGeographySchema


class MachineService(CRUDService):
    manager_class = MachineManager
    filter_class = MachineFilter

    async def get_machines_count_per_geography(self, query_filter: MachineFilter) -> Page[MachinesCountGeographySchema]:
        return await self.manager.get_machines_count_per_geography(query_filter)
