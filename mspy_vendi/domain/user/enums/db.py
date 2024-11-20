from sqlalchemy import Enum

from .enum import PermissionEnum, RoleEnum, StatusEnum

role_db_enum = Enum(
    *[role.value for role in RoleEnum],
    name="role_db_enum",
)

status_db_enum = Enum(
    *[status.value for status in StatusEnum],
    name="status_db_enum",
)

permission_db_enum = Enum(
    *[permission.value for permission in PermissionEnum],
    name="permission_db_enum",
)
