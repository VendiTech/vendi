from datetime import date

from domain.impressions.schemas import CreateImpressionSchema
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

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

    async def create_batch(self, obj: list[CreateImpressionSchema]) -> None:
        """
        Create a batch of impressions in the database.

        :param obj: A list of impressions to create.
        """
        try:
            stmt = insert(self.sql_model)

            await self.session.execute(stmt, [item.model_dump() for item in obj])
            await self.session.commit()

        except Exception as ex:
            await self.session.rollback()
            raise ex
