from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from mspy_vendi.config import config
from mspy_vendi.core.middlewares.error_middleware import ErrorMiddleware
from mspy_vendi.core.middlewares.execution_middleware import measure_execution_time


def init_middlewares(app: FastAPI) -> FastAPI:
    """
    Wrap FastAPI application, with various of middlewares

    **NOTE** Middlewares are executed in the reverse order of their addition. Similar to LIFO stack, not FIFO queue.
    For example, All middlewares must depend on the CORSMiddleware, that's why new middlewares must be added before.
    Middleware for measuring request's execution time should be added after CORS middleware.

    To ensure that all unprocessed errors are caught and that other middleware logic is applied correctly,
    the ErrorMiddleware should be added last.
    """
    app.add_middleware(ErrorMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=measure_execution_time)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.methods,
        allow_headers=config.cors.headers,
    )
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=("mspy_vendi.core.middlewares.debug_toolbar.SQLAlchemyPanel",),
        settings=(config,),
    )

    return app
