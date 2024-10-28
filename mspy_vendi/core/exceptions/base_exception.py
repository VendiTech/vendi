import json
from typing import Any, LiteralString, NoReturn, Type

from fastapi.exceptions import RequestValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError
from sqlalchemy.exc import DBAPIError
from starlette import status

from mspy_vendi.config import config
from mspy_vendi.core.enums import AppEnvEnum, PGErrorCodeEnum

type HttpCode = int
# mypy: disable-error-code="dict-item"


class BaseError(Exception):
    """
    Base error class
    """

    title: str
    default_detail: str
    content: dict
    status_code: HttpCode

    def __init__(self, detail: str | None = None):
        self.content = {
            "title": self.title,
            "detail": detail or self.default_detail,
        }

    def __str__(self) -> str:
        return json.dumps(self.content)


class BadRequestError(BaseError):
    """
    The server cannot or will not process the request due to an apparent client error
    """

    title = "Bad Request"
    default_detail = "The server cannot process the request from the client"
    status_code = status.HTTP_400_BAD_REQUEST


class ForbiddenError(BaseError):
    """
    The client does not have access rights to the content
    """

    title = "Forbidden"
    default_detail = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN


class UnauthorizedError(BaseError):
    """
    The client must authenticate itself to get the requested response
    """

    title = "Unauthorized"
    default_detail = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED


class UnprocessableEntityError(BaseError):
    """
    The request was well-formed but was unable to be followed due to semantic errors
    """

    title = "Unprocessable Entity"
    default_detail = "Unprocessable Entity"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class NotFoundError(BaseError):
    """
    The server can not find the requested resource
    """

    title = "Not Found"
    default_detail = "Not Found"
    status_code = status.HTTP_404_NOT_FOUND


class RequestTimeoutError(BaseError):
    """
    The server would like to shut down this unused connection
    """

    title = "Request Timeout"
    default_detail = "Request Timeout"
    status_code = status.HTTP_408_REQUEST_TIMEOUT


class ConflictError(BaseError):
    """
    The request could not be completed due to a conflict with the current state of the resource
    """

    title = "Conflict"
    default_detail = "Some of the provided fields are already in use. Please use different values"
    status_code = status.HTTP_409_CONFLICT


class ServerError(BaseError):
    """
    The request could not be completed due to a server issue
    """

    title = "Internal Server Error"
    default_detail = "Internal Server Error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ForeignKeyError(UnprocessableEntityError):
    """
    The request couldn't be completed due to a ForeignKey error
    """

    default_detail = "Related entity conflict"


class DuplicatesError(BadRequestError):
    """
    The request couldn't be completed due to a DuplicatesError error
    """

    default_detail = "Duplicate error"


class NotNullViolationError(UnprocessableEntityError):
    """
    The request couldn't be completed due to a NotNullViolationError error
    """

    default_detail = "Required field is missing"


class LogicalConstraintViolationError(UnprocessableEntityError):
    """
    The request couldn't be completed due to a LogicalConstraintViolationError error
    """

    default_detail = "Logical constraint violation"


class PydanticLikeError(RequestValidationError):
    def __init__(self, message: LiteralString, location: tuple, input_: Any) -> None:
        errors = (
            ValidationError.from_exception_data(
                "ValueError",
                [
                    InitErrorDetails(
                        type=PydanticCustomError("value_error", message),
                        loc=location,
                        input=input_,
                    )
                ],
            )
        ).errors()
        super().__init__(errors)


db_error_mapping: dict[PGErrorCodeEnum, Type[BaseError]] = {
    PGErrorCodeEnum.NOT_NULL_VIOLATION: NotNullViolationError,
    PGErrorCodeEnum.CONSTRAINT_VIOLATION: LogicalConstraintViolationError,
    PGErrorCodeEnum.FOREIGN_KEY_VIOLATION: ForeignKeyError,
    PGErrorCodeEnum.UNIQUE_VIOLATION: ConflictError,
}


def raise_db_error(ex: DBAPIError) -> NoReturn:
    """
    Raises a more specific database error based on the given DBAPIError exception.

    :param ex: The DBAPIError exception to be handled.

    :raise: A more specific error based on the error mapping,
            or re-raises the original error if the "pgcode" is not found in the mapping.
    """

    if (error_class := db_error_mapping.get(ex.orig.pgcode)) is not None:
        exception_message: tuple[str, ...] = ex.orig.args

        errors = [
            error_class.default_detail,
            f"Error: {', '.join(exception_message)}"
            if exception_message and config.environment not in [AppEnvEnum.PRD, AppEnvEnum.STG]
            else None,
        ]

        raise error_class(". ".join(filter(None, errors)))

    raise ex
