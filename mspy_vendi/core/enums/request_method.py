from enum import StrEnum, unique


@unique
class RequestMethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
