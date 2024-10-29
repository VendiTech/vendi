import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from uvicorn import Server

from mspy_vendi.api import init_routers
from mspy_vendi.config import Settings, config
from mspy_vendi.core.exceptions import exception_handlers
from mspy_vendi.core.middlewares import init_middlewares

logger = logging.getLogger(__name__)


class WebServer:
    @classmethod
    async def build_server(cls):
        app = cls.get_app()

        u_config = uvicorn.Config(
            app,
            host=config.web.host,
            port=config.web.port,
            reload=config.web.is_reload,
            log_level=config.web.log_level,
            workers=config.web.workers,
            limit_concurrency=config.web.limit_concurrency,
        )
        u_config.load()

        return uvicorn.Server(config=u_config)

    @classmethod
    def get_app(cls) -> FastAPI:
        _app = FastAPI(
            title=config.title,
            version=config.version,
            exception_handlers=exception_handlers,
            debug=config.debug,
            docs_url=config.docs_url,
        )

        init_routers(_app)
        init_middlewares(_app)
        add_pagination(_app)

        return _app

    @classmethod
    async def web_server(cls):
        server = await cls.build_server()
        logger.info(f"Starting server on {config.web.listen_address}")

        await server.serve()

app = WebServer.get_app()

if __name__ == "__main__":
    asyncio.run(WebServer.web_server())
