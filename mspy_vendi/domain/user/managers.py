from mspy_vendi.core.manager import CRUDManager
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
