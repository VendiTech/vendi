from typing import TYPE_CHECKING, Optional

from mspy_vendi.config import log
from mspy_vendi.core.exceptions.base_exception import ForbiddenError, UnauthorizedError

if TYPE_CHECKING:
    from mspy_vendi.domain.user.models import User


def check_auth_criteria(
    user: Optional["User"],
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    is_verified: bool | None = None,
    is_active_license: bool | None = None,
) -> "User":
    """
    Check if the user meets the criteria for the given parameters.

    We raise different types of exceptions based on the communication type.

    :param user: The user to check.
    :param is_active: Parameter to check if the user is active.
    :param is_superuser: Parameter to check if the user is a superuser.
    :param is_verified: Parameter to check if the user is verified.
    :param is_active_license: Parameter to check if the user has the license.

    :return: The user if the criteria is met.
    :raises UnauthorizedError: If the user does not meet the criteria.
    """
    if not user:
        raise UnauthorizedError("Invalid credentials")

    user_attributes: dict[str, bool | None] = {
        "is_active": is_active,
        "is_superuser": is_superuser,
        "is_verified": is_verified,
        "is_active_license": is_active_license,
    }

    for attribute, expected_value in user_attributes.items():
        if expected_value is not None and expected_value != getattr(user, attribute):
            log.error(
                "Permission check doesn't pass. "
                f"Detail: {attribute=!r}, {expected_value=!r}, actual_value={getattr(user, attribute)}",
                user_id=user.id,
            )

            raise ForbiddenError
    return user
