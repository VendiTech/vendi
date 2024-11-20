from typing import Any

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import update
from sqlalchemy.orm import joinedload

from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.core.manager import CRUDManager, UpdateSchema
from mspy_vendi.core.pagination import Page
from mspy_vendi.domain.machines.models import MachineUser
from mspy_vendi.domain.user.enums import PermissionEnum
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserListSchema


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
        self, obj_id: int, obj: UpdateSchema, autocommit: bool = True, is_unique: bool = False, **_: Any
    ) -> User:
        """
        Updates an object.

        :param obj: The object to update.
        :param obj_id: The ID of the object to update.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param kwargs: Additional keyword arguments.

        :returns: The updated object.
        """
        if not (updated_model := obj.model_dump(exclude_defaults=True, exclude={"machines"})):
            raise BadRequestError("No data provided for updating")

        stmt = (
            update(self.sql_model).where(self.sql_model.id == obj_id).values(**updated_model).returning(self.sql_model)
        )

        return await self._apply_changes(stmt=stmt, obj_id=obj_id, autocommit=autocommit, is_unique=is_unique)

    async def get_all(
        self,
        query_filter: BaseFilter | None = None,
        raw_result: bool = False,
        is_unique: bool = False,
        **_: Any,
    ) -> Page[UserListSchema] | list[User]:
        """
        This method retrieves all objects from the database.

        :param query_filter: A SQLAlchemy Filter object to filter the objects to be retrieved. If None, no filter will
                             be applied. Default is None.
        :param raw_result: A flag that determines whether to return a list of raw results without pagination.
                           If True, a list of raw results will be returned.
                           If False, a Page object with paginated results will be returned. Default is False.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.

        :return: A Page object with paginated results if raw_result is False, otherwise a list of raw results.

        :raises NoResultFound: If no objects are found in the database.
        """
        stmt = self.get_query().options(joinedload(self.sql_model.machine_users).joinedload(MachineUser.machine))

        if query_filter:
            stmt = query_filter.filter(stmt)
            stmt = query_filter.sort(stmt)

        if raw_result:
            if is_unique:
                return (await self.session.execute(stmt)).unique().all()  # type: ignore

            return (await self.session.scalars(stmt)).all()  # type: ignore

        return await paginate(self.session, stmt)
