from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import joinedload

from mspy_vendi.core.manager import CRUDManager, Model, Schema
from mspy_vendi.db import Sale


class SaleManager(CRUDManager):
    sql_model = Sale

    async def get_all(
        self,
        query_filter: Filter | None = None,
        raw_result: bool = False,
        is_unique: bool = False,
        **_: Any,
    ) -> Page[Schema] | list[Model]:
        stmt = self.get_query().options(
            joinedload(Sale.product),
            joinedload(Sale.machine),
        )

        if query_filter:
            stmt = query_filter.filter(stmt)
            stmt = query_filter.sort(stmt)

        if raw_result:
            if is_unique:
                return (await self.session.execute(stmt)).unique().all()  # type: ignore

            return (await self.session.scalars(stmt)).all()  # type: ignore

        return await paginate(self.session, stmt)
