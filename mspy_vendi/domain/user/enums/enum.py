from enum import StrEnum


class RoleEnum(StrEnum):
    ADMIN = "admin"
    USER = "user"


class PermissionEnum(StrEnum):
    ANY = "any"
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class StatusEnum(StrEnum):
    """
    This enum represents every account's status.
    """

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class FrontendLinkEnum(StrEnum):
    EMAIL_VERIFY = "registration-confirmation"
    PASSWORD_RESET = "reset-password"
    LOG_IN = "sign-in"
