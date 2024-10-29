from fastapi.exceptions import RequestValidationError

from .base_exception import BaseError
from .error_handlers import base_error_handler, request_validation_error_handler, value_error_handler

exception_handlers = {
    RequestValidationError: request_validation_error_handler,
    ValueError: value_error_handler,
    BaseError: base_error_handler,
}

__all__ = ("exception_handlers",)
