import sentry_sdk
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sentry_sdk.integrations.logging import ignore_logger

from mspy_vendi.config import log
from mspy_vendi.core.exceptions.base_exception import BaseError

# Turn off Sentry logging tracking for this module
ignore_logger(__name__)


async def request_validation_error_handler(_: Request, exc: RequestValidationError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Validation error",
            "detail": jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        },
    )


async def validation_error_handler(_: Request, exc: ValidationError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Validation error",
            "detail": exc.json(),
        },
    )


async def value_error_handler(_: Request, exc: ValueError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": status.HTTP_400_BAD_REQUEST,
            "title": "Bad Request error",
            "detail": "The server cannot process the request from the client",
        },
    )


async def base_error_handler(_: Request, exc: BaseError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.content,
    )
