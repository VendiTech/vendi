from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from mspy_vendi.config import log
from mspy_vendi.core.exceptions.base_exception import BaseError


async def validation_error_handler(_: Request, exc: ValidationError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": "Validation error",
            "detail": exc.errors()
        },
    )


async def base_error_handler(_: Request, exc: BaseError):
    log.info(f"{exc.__class__.__name__}", error=str(exc))

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.content,
    )
