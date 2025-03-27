from typing import Any

from sqlalchemy import Select, update
from sqlalchemy.orm import joinedload

from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.core.manager import CRUDManager, UpdateSchema
from mspy_vendi.domain.machines.models import MachineUser
from mspy_vendi.domain.product_user.models import ProductUser
from mspy_vendi.domain.user.enums import PermissionEnum
from mspy_vendi.domain.user.models import User


class UserManager(CRUDManager):
    sql_model = User

    async def update_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        """
        Update the permissions of the user.
        Check if the permissions are already present in the user's permissions.
        And merge the permissions with the user's permissions.

        :param modified_user: The user to update.
        :param permissions: The permissions to update.

        :return: The updated user.
        """
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) | set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user

    async def delete_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        """
        Delete the permissions of the user.
        Check if the permissions are already present in the user's permissions.
        And subtract the permissions with the user's permissions.

        :param modified_user: The user to update.
        :param permissions: The permissions to update.

        :return: The updated user.
        """
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) - set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user

    async def update(
        self,
        obj_id: int,
        obj: UpdateSchema,
        autocommit: bool = True,
        is_unique: bool = False,
        raise_error: bool = True,
        **_: Any,
    ) -> User:
        """
        Updates an object.

        :param obj: The object to update.
        :param obj_id: The ID of the object to update.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param raise_error: If True, raise an error if the object is not found, otherwise return None.
        :param kwargs: Additional keyword arguments.

        :returns: The updated object.
        """
        if (
            not (updated_model := obj.model_dump(exclude_defaults=True, exclude={"machines", "products"}))
            and raise_error
        ):
            raise BadRequestError("No data provided for updating")

        stmt = (
            update(self.sql_model).where(self.sql_model.id == obj_id).values(**updated_model).returning(self.sql_model)
        )

        return await self._apply_changes(stmt=stmt, obj_id=obj_id, autocommit=autocommit, is_unique=is_unique)

    def get_query(self) -> Select:
        return (
            super()
            .get_query()
            .options(joinedload(self.sql_model.machine_users).joinedload(MachineUser.machine))
            .options(joinedload(self.sql_model.product_users).joinedload(ProductUser.product))
        )
