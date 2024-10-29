from enum import IntEnum, StrEnum, unique


@unique
class CRUDEnum(IntEnum):
    """
    Enum for CRUD operations
    This enum is used to turn on / off CRUD operations in the "CRUDApi" class via the "endpoints" attribute
    """

    CREATE = 0
    GET = 1
    LIST = 2
    UPDATE = 3
    DELETE = 4


class HealthCheckStatusEnum(StrEnum):
    SUCCESS = "Success"
    FAILURE = "Failure"
