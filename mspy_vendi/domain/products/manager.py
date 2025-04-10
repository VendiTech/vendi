from sqlalchemy import select

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import Product


class ProductManager(CRUDManager):
    sql_model = Product

    async def get_by_name(self, name: str) -> Product | None:
        stmt = select(self.sql_model).where(self.sql_model.name == name)

        return await self.session.scalar(stmt)
