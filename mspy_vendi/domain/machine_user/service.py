from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.machine_user.manager import MachineUserManager
from mspy_vendi.domain.machines.manager import MachineManager
from mspy_vendi.domain.user.managers import UserManager


class MachineUserService(CRUDService):
    manager_class = MachineUserManager

    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
        self.user_manager = UserManager(db_session)
        self.machine_manager = MachineManager(db_session)
        super().__init__(db_session=db_session)

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

    async def attach_all_machines(self, user_id: int) -> None:
        """
        Attach all machines to the user.

        :param user_id: The user ID.
        """
        # Check if the provided user_id exists
        await self.user_manager.get(user_id)

        current_machines_set: set[int] = set(await self.manager.get_machines_for_user(user_id=user_id))
        all_machines_set: set[int] = set(await self.machine_manager.get_all_machine_ids())

        if machines_to_add := all_machines_set - current_machines_set:
            await self.manager.attach_user_to_machine(user_id, *machines_to_add)
