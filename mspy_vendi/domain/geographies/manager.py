from sqlalchemy import select

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import Geography
from mspy_vendi.domain.geographies.schemas import CreateGeographySchema


class GeographyManager(CRUDManager):
    sql_model = Geography

    async def get_by_name(self, name: str) -> Geography | None:
        stmt = select(self.sql_model).where(self.sql_model.name == name)

        return await self.session.scalar(stmt)

    async def get_or_create(self, obj: CreateGeographySchema, name: str | None = None) -> tuple[Geography, bool]:
        """
        Get or create an entity in the database, and returns the DB object.

        :param obj: Pydantic `CreateSchema` model.
        :param name: Object Name.

        :return: tuple of boolean and created entity.
        """
        if result := await self.get_by_name(name=name):
            return result, False

        return await self.create(obj), True
