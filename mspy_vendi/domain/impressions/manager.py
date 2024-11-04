from datetime import date

from sqlalchemy import select

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import Impression


class ImpressionManager(CRUDManager):
    sql_model = Impression

    async def get_latest_impression_date(self, device_number: str) -> date | None:
        """
        Get the date of the latest impression in the database.

        :return: The date of the latest impression or None if no impressions are found.
        """
        stmt = select(self.sql_model.date).order_by(self.sql_model.date.desc()).limit(1)

        return await self.session.scalar(stmt)
