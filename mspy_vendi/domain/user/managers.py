from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.user.enums import PermissionEnum
from mspy_vendi.domain.user.models import User


class UserManager(CRUDManager):
    sql_model = User

    async def update_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) | set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user

    async def delete_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) - set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user
