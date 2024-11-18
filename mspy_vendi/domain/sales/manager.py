from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import CTE, Date, Select, cast, func, label, select, text
from sqlalchemy.orm import joinedload

from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.exceptions.base_exception import NotFoundError
from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.core.manager import CRUDManager, Model, Schema
from mspy_vendi.db import Sale
from mspy_vendi.domain.geographies.models import Geography
from mspy_vendi.domain.machines.models import Machine
from mspy_vendi.domain.product_category.models import ProductCategory
from mspy_vendi.domain.products.models import Product
from mspy_vendi.domain.sales.filter import SaleFilter, StatisticDateRangeFilter
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    TimeFrameSalesSchema,
)


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

    def _generate_geography_query(self, query_filter: BaseFilter, stmt: Select) -> Select:
        """
        Generate query to filter by geography_id field.
        It makes a join with Machine and Geography tables to filter by geography_id field.

        :param query_filter: Filter object.
        :param stmt: Current statement.

        :return: New statement with the filter applied.
        """
        if query_filter.geography_id__in:
            stmt = (
                stmt.join(Machine, Machine.id == self.sql_model.machine_id)
                .join(Geography, Geography.id == Machine.geography_id)
                .where(Geography.id.in_(query_filter.geography_id__in))
            )
            # We do it to ignore the field inside the filter block
            setattr(query_filter, "geography_id__in", None)

        return stmt

    @staticmethod
    def _generate_date_range_cte(time_frame: DateRangeEnum, query_filter: StatisticDateRangeFilter) -> CTE:
        """
        Generate CTE with date range.
        It uses generate_series function to generate a range of dates between date_from and date_to.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: CTE with the date range.
        """
        return select(
            func.generate_series(
                func.date_trunc(time_frame.value, cast(query_filter.date_from, Date)),
                cast(query_filter.date_to, Date),
                text(f"'1 {time_frame}'"),
            ).label("time_frame")
        ).cte()

    async def get_sales_quantity_by_product(self, query_filter: SaleFilter) -> BaseQuantitySchema:
        """
        Get the total quantity of sales by product|s.
        Calculate the sum of the quantity field. If no sales are found, raise a NotFoundError.

        :param query_filter: Filter object.

        :return: Total quantity of sales.
        """
        stmt = select(func.sum(self.sql_model.quantity).label("quantity"))

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        if (
            not (result := (await self.session.execute(stmt)).mappings().one_or_none())
            or result.get("quantity") is None
        ):
            raise NotFoundError(detail="No sales were find.")

        return result  # type: ignore

    async def get_sales_quantity_per_range(
        self, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[TimeFrameSalesSchema]:
        """
        Get the total quantity of sales per time frame.
        Calculate the sum of the quantity field and group by the time frame.
        If no sales are found, raise a NotFoundError.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: Total quantity of sales per time frame.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.sale_date))
        stmt_sum_quantity = label("quantity", func.sum(self.sql_model.quantity))

        stmt = select(stmt_time_frame, stmt_sum_quantity).group_by(stmt_time_frame).order_by(stmt_time_frame)

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)
        stmt = stmt.subquery()

        date_range_cte = self._generate_date_range_cte(time_frame, query_filter)

        final_stmt = (
            select(date_range_cte.c.time_frame, func.coalesce(stmt.c.quantity, 0).label("quantity"))
            .select_from(date_range_cte)
            .outerjoin(stmt, stmt.c.time_frame == date_range_cte.c.time_frame)
            .order_by(date_range_cte.c.time_frame)
        )

        return await paginate(self.session, final_stmt)

    async def get_average_sales_across_machines(self, query_filter: SaleFilter) -> DecimalQuantitySchema:
        """
        Get the average quantity of sales across machines.
        Calculate the average of the quantity field. If no sales are found, raise a NotFoundError.

        :param query_filter: Filter object.

        :return: Average quantity of sales.
        """
        stmt = select(func.avg(self.sql_model.quantity).label("quantity"))

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        if (
            not (result := (await self.session.execute(stmt)).mappings().one_or_none())
            or result.get("quantity") is None
        ):
            raise NotFoundError(detail="No sales were find.")

        return result  # type: ignore

    async def get_average_sales_per_range(
        self, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[DecimalTimeFrameSalesSchema]:
        """
        Get the average quantity of sales per time frame.
        Calculate the average of the quantity field and group by the time frame.
        If no sales are found, raise a NotFoundError.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: Average quantity of sales per time frame.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.sale_date))
        stmt_avg_quantity = label("quantity", func.avg(self.sql_model.quantity))

        stmt = select(stmt_time_frame, stmt_avg_quantity).group_by(stmt_time_frame)

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)
        stmt = stmt.subquery()

        date_range_cte = self._generate_date_range_cte(time_frame, query_filter)

        final_stmt = (
            select(date_range_cte.c.time_frame, func.coalesce(stmt.c.quantity, 0).label("quantity"))
            .select_from(date_range_cte)
            .outerjoin(stmt, stmt.c.time_frame == date_range_cte.c.time_frame)
            .order_by(date_range_cte.c.time_frame)
        )

        return await paginate(self.session, final_stmt)

    async def get_sales_quantity_per_category(self, query_filter: SaleFilter) -> Page[CategoryProductQuantitySchema]:
        """
        Get the sales quantity for each product category.

        :param query_filter: Filter object.
        :return: A paginated list with each product category's quantity.
        """
        stmt_category_name = label("category_name", ProductCategory.name)
        stmt_category_id = label("category_id", ProductCategory.id)
        stmt_sum_category_quantity = label("quantity", func.sum(self.sql_model.quantity))

        stmt = (
            select(stmt_category_id, stmt_category_name, stmt_sum_category_quantity)
            .join(Product, Product.id == self.sql_model.product_id)
            .join(ProductCategory, ProductCategory.id == Product.product_category_id)
            .group_by(stmt_category_name, stmt_category_id)
            .order_by(stmt_sum_category_quantity.desc())
        )

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt)

    async def get_sales_category_quantity_per_time_frame(
        self, query_filter: SaleFilter
    ) -> Page[CategoryTimeFrameSalesSchema]:
        """
        Get the sales quantity per day for each product category.

        :param query_filter: Filter object.
        :return: A paginated list with each product category's sales quantity over time.
        """
        stmt_category_name = label("category_name", ProductCategory.name)
        stmt_category_id = label("category_id", ProductCategory.id)
        stmt_sale_date = label("time_frame", func.date_trunc("day", self.sql_model.sale_date))
        stmt_sum_quantity = label("quantity", func.sum(self.sql_model.quantity))

        subquery = (
            select(stmt_category_id, stmt_category_name, stmt_sale_date, stmt_sum_quantity)
            .join(Product, Product.id == self.sql_model.product_id)
            .join(ProductCategory, ProductCategory.id == Product.product_category_id)
            .group_by(stmt_category_name, stmt_sale_date, stmt_category_id)
            .order_by(stmt_category_name, stmt_sale_date)
        )

        subquery = self._generate_geography_query(query_filter, subquery)
        subquery = query_filter.filter(subquery).subquery()

        stmt = (
            select(
                func.jsonb_build_object(
                    "category_id",
                    subquery.c.category_id,
                    "category_name",
                    subquery.c.category_name,
                    "sale_range",
                    func.array_agg(
                        func.jsonb_build_object("time_frame", subquery.c.time_frame, "quantity", subquery.c.quantity)
                    ),
                )
            )
            .group_by(subquery.c.category_name, subquery.c.category_id)
            .order_by(subquery.c.category_name)
        )

        return await paginate(self.session, stmt, unique=False)
