from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.machine_user.manager import MachineUserManager


class MachineUserService(CRUDService):
    manager_class = MachineUserManager

    async def update_user_machines(self, user_id: int, *machine_ids: int) -> None:
        """
        Update the machines of the user.

        :param user_id: The user ID.
        :param machine_ids: The machine IDs.
        """
        current_machines_set: set[int] = set(await self.manager.get_machines_for_user(user_id=user_id))
        new_machines_set: set[int] = set(machine_ids)

        if machines_to_add := new_machines_set - current_machines_set:
            await self.manager.attach_user_to_machine(user_id, *machines_to_add)

        if machines_to_remove := current_machines_set - new_machines_set:
            await self.manager.disassociate_user_with_machine(user_id, *machines_to_remove)
