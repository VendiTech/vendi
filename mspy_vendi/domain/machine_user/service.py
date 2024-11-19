from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.machine_user.manager import MachineUserManager


class MachineUserService(CRUDService):
    manager_class = MachineUserManager

    async def attach_user_to_machine(self, user_id: int, *machine_ids: int) -> None:
        return await self.manager.attach_user_to_machine(user_id, *machine_ids)

    async def disassociate_user_with_machine(self, user_id: int, *machine_ids: int) -> None:
        return await self.manager.disassociate_user_with_machine(user_id, *machine_ids)
