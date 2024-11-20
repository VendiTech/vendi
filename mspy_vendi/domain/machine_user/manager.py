from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError

from mspy_vendi.core.exceptions.base_exception import raise_db_error
from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.machines.models import MachineUser


class MachineUserManager(CRUDManager):
    sql_model = MachineUser

    async def attach_user_to_machine(self, user_id: int, *machine_ids: int) -> None:
        try:
            await self.session.execute(
                insert(self.sql_model),
                [dict(user_id=user_id, machine_id=machine_id) for machine_id in set(machine_ids)],
            )
            await self.session.commit()

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

    async def disassociate_user_with_machine(self, user_id: int, *machine_ids: int) -> None:
        try:
            await self.session.execute(
                delete(self.sql_model).where(
                    self.sql_model.user_id == user_id, self.sql_model.machine_id.in_(machine_ids)
                ),
            )
            await self.session.commit()

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

    async def get_machines_for_user(self, user_id: int) -> list[int]:
        stmt = select(self.sql_model.machine_id).where(self.sql_model.user_id == user_id)

        return (await self.session.scalars(stmt)).all()  # type: ignore
