from typing import Optional

from sqlalchemy import select

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import ProductCategory
from mspy_vendi.domain.product_category.schemas import CreateProductCategorySchema


class ProductCategoryManager(CRUDManager):
    sql_model = ProductCategory

    async def get_by_name(self, name: str) -> ProductCategory | None:
        stmt = select(self.sql_model).where(self.sql_model.name == name)

        return await self.session.scalar(stmt)

    async def get_or_create(
        self, obj: CreateProductCategorySchema, name: str | None = None
    ) -> tuple[ProductCategory, bool]:
        """
        Get or create an entity in the database, and returns the DB object.

        :param obj: Pydantic `CreateSchema` model.
        :param name: Object Name.

        :return: tuple of boolean and created entity.
        """
        if result := await self.get_by_name(name=name):
            return result, False

        return await self.create(obj), True

    async def update_or_create(
        self,
        obj: CreateProductCategorySchema,
        name: str | None = None,
    ) -> tuple[ProductCategory, Optional[ProductCategory], bool]:
        """
        Update or create an entity in the database, and returns the DB object.

        :param obj: Pydantic `CreateSchema` model.
        :param name: Object Name.

        :return: tuple of boolean and created entity.
        """
        if product_category := await self.get_by_name(name=name):
            result = await self.update(product_category.id, obj=obj)
            return result, product_category, True

        return await self.create(obj=obj), None, False
