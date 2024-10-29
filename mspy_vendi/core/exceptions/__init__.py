from fastapi.exceptions import RequestValidationError

from .base_exception import BaseError
from .error_handlers import base_error_handler, validation_error_handler

exception_handlers = {
    RequestValidationError: validation_error_handler,
    BaseError: base_error_handler,
}

__all__ = ("exception_handlers",)
