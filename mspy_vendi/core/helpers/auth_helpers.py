from typing import TYPE_CHECKING, Optional

from mspy_vendi.config import log
from mspy_vendi.core.exceptions.base_exception import ForbiddenError, UnauthorizedError
from mspy_vendi.domain.user.enums import PermissionEnum, StatusEnum

if TYPE_CHECKING:
    from mspy_vendi.domain.user.models import User


def check_auth_criteria(
    user: Optional["User"],
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    is_verified: bool | None = None,
    permissions: list[PermissionEnum] | None = None,
) -> "User":
    """
    Check if the user meets the criteria for the given parameters.

    Here are the criteria that are checked:
    - If the user is active.
    - If the user is a superuser.
    - If the user is verified.
    - If the user has the valid permissions.


    :param user: The user to check.
    :param is_active: Parameter to check if the user is active.
    :param is_superuser: Parameter to check if the user is a superuser.
    :param is_verified: Parameter to check if the user is verified.
    :param permissions: Parameter to check if the user has the valid permissions.

    :return: The user if the criteria is met.
    :raises UnauthorizedError: If the user does not meet the criteria.
    """
    if not user:
        raise UnauthorizedError("Invalid credentials")

    if is_superuser and permissions:
        log.debug(
            "You don't need to provide both is_superuser and permissions."
            "Hint: if you provide `is_superuser=True` - permissions check is redundant.",
        )

    if user.status in [StatusEnum.SUSPENDED, StatusEnum.DELETED]:
        log.error("User is suspended or deleted.", user_id=user.id)
        raise ForbiddenError

    if user.is_superuser:
        log.debug("Current user is Super User. All checks are skipped.", user_id=user.id)
        return user

    user_attributes: dict[str, bool | None] = {
        "is_active": is_active,
        "is_superuser": is_superuser,
        "is_verified": is_verified,
    }

    for attribute, expected_value in user_attributes.items():
        if expected_value is not None and expected_value != getattr(user, attribute):
            log.error(
                "Permission check doesn't pass. "
                f"Detail: {attribute=!r}, {expected_value=!r}, actual_value={getattr(user, attribute)}",
                user_id=user.id,
            )

            raise ForbiddenError

    if permissions and not any(
        (user_permission in permissions or user_permission == PermissionEnum.ANY)
        for user_permission in user.permissions
    ):
        log.error(
            "Permission check doesn't pass. "
            f"Detail: needed_permissions={permissions=!r}, user_permissions={user.permissions}",
            user_id=user.id,
        )

        raise ForbiddenError

    return user
