from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.config import log
from mspy_vendi.deps import get_db_session


class HealthCheckService:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]):
        self.session = session

    async def check_database_connection(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
            return True

        except Exception as exc_info:
            log.error(f"Database connection error: {exc_info}")

            return False
