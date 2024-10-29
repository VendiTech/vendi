from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from mspy_vendi.config import config, log

engine: AsyncEngine = create_async_engine(
    config.db.db_url, pool_size=config.db.pool_size, max_overflow=config.db.max_overflow
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Ideally for tests
AsyncScopedSession = async_scoped_session(AsyncSessionLocal, scopefunc=current_task)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionLocal()
    try:
        yield session

    except SQLAlchemyError as exc:
        log.error("DB exception occurred, rolling back transaction", exception=str(exc))
        await session.rollback()

        raise exc

    finally:
        await session.close()
