from datetime import time
from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import CTE, Date, Select, cast, desc, func, label, select, text
from sqlalchemy.orm import joinedload

from mspy_vendi.core.enums.date_range import DailyTimePeriodEnum, DateRangeEnum, TimePeriodEnum
from mspy_vendi.core.exceptions.base_exception import NotFoundError
from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.core.manager import CRUDManager, Model, Schema
from mspy_vendi.db import Sale
from mspy_vendi.domain.geographies.models import Geography
from mspy_vendi.domain.machines.models import Machine, MachineUser
from mspy_vendi.domain.product_category.models import ProductCategory
from mspy_vendi.domain.products.models import Product
from mspy_vendi.domain.sales.filters import ExportSaleFilter, SaleFilter, StatisticDateRangeFilter
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantityDateSchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    TimePeriodSalesRevenueSchema,
    UnitsTimeFrameSchema,
    VenueSalesQuantitySchema,
)
from mspy_vendi.domain.user.models import User


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

    def _generate_user_filtration_query(self, user: User, stmt: Select) -> Select:
        """
        Generate a query to filter by machine_id related to current User

        :param user: Current User.
        :param stmt: Current statement.
        :return: New statement with the filter applied.
        """
        return (
            stmt.join(Machine, Machine.id == self.sql_model.machine_id)
            .join(MachineUser, MachineUser.machine_id == Machine.id)
            .where(MachineUser.user_id == user.id)
        )

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
                text(f"'{time_frame.interval}'"),
            ).label("time_frame")
        ).cte()

    @staticmethod
    def _get_time_periods(
        time_period: type[TimePeriodEnum] | type[DailyTimePeriodEnum],
    ) -> dict[str, tuple[time, time]]:
        """
        Generate a dictionary mapping time period names to start and end times.

        :param time_period: An enum class defining time periods.
        :return: A dictionary where keys are period names and values are tuples of (start_time, end_time).
        """
        return {period.name: (period.start, period.end) for period in time_period}

    async def get_sales_quantity_by_product(self, query_filter: SaleFilter) -> BaseQuantitySchema:
        """
        Get the total quantity of sales by product|s.
        Calculate the sum of the quantity field. If no sales are found, raise a NotFoundError.

        :param user: Current user.
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
        self,
        time_frame: DateRangeEnum,
        query_filter: SaleFilter,
    ) -> Page[TimeFrameSalesSchema]:
        """
        Get the total quantity of sales per time frame.
        Calculate the sum of the quantity field and group by the time frame.
        If no sales are found, raise a NotFoundError.

        :param user: Current user.
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

        :param user: Current user.
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
        self,
        time_frame: DateRangeEnum,
        query_filter: SaleFilter,
    ) -> Page[DecimalTimeFrameSalesSchema]:
        """
        Get the average quantity of sales per time frame.
        Calculate the average of the quantity field and group by the time frame.
        If no sales are found, raise a NotFoundError.

        :param user: Current user.
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

        :param user: Current user.
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
        self,
        query_filter: SaleFilter,
    ) -> Page[CategoryTimeFrameSalesSchema]:
        """
        Get the sales quantity per day for each product category.

        :param user: Current user.
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

    async def get_sales_count_per_time_period(
        self,
        time_period: type[DailyTimePeriodEnum],
        query_filter: SaleFilter,
    ) -> list[TimePeriodSalesCountSchema]:
        """
        Get the sales count for each time frame.
        e.g (6 AM - 6 PM, 6 PM - 8 PM, 8 AM - 10 PM, 10 PM - 12 AM, 12 AM - 2 AM, 2 AM - 6 AM).

        :param time_period: Enum object to map sales.
        :param user: Current user.
        :param query_filter: Filter object.

        :return: A list with sales count for each time period.
        """
        time_periods = self._get_time_periods(time_period)

        stmt = select(self.sql_model.sale_time)

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        result = await self.session.execute(stmt)
        sale_times = [row.sale_time for row in result.fetchall()]

        sales_by_period = {period: 0 for period in time_periods.keys()}

        for sale_time in sale_times:
            for period_name, (start, end) in time_periods.items():
                if start <= sale_time <= end:
                    sales_by_period[period_name] += 1
                    break

        return [{"time_period": period, "sales": count} for period, count in sales_by_period.items()]  # type: ignore

    async def get_sales_revenue_per_time_period(
        self,
        time_period: type[TimePeriodEnum],
        query_filter: SaleFilter,
    ) -> list[TimePeriodSalesRevenueSchema]:
        """
        Get the total sales revenue (quantity * price) for each time frame.

        :param time_period: Enum object to map sales.
        :param query_filter: Filter object.
        :return: A list with sales revenue for each time period.
        """
        time_periods = self._get_time_periods(time_period)

        stmt = select(self.sql_model.sale_time, (self.sql_model.quantity * Product.price).label("revenue")).join(
            Product, Product.id == self.sql_model.product_id
        )

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        result = await self.session.execute(stmt)
        rows = result.fetchall()

        revenue_by_period = {period: 0 for period in time_periods.keys()}

        for row in rows:
            sale_time, revenue = row.sale_time, row.revenue
            for period_name, (start, end) in time_periods.items():
                if start <= sale_time <= end:
                    revenue_by_period[period_name] += revenue
                    break

        return [{"time_period": period, "revenue": total} for period, total in revenue_by_period.items()]  # type: ignore

    async def get_units_sold(self, time_frame: DateRangeEnum, query_filter: SaleFilter) -> Page[UnitsTimeFrameSchema]:
        """
        Get the units (quantity * price) sold per each time frame.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: Paginated list of units sold per each time frame.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.sale_date))
        stmt_units = label("units", func.sum(self.sql_model.quantity * Product.price))

        sales_subquery = (
            select(stmt_time_frame, stmt_units)
            .join(Product, Product.id == self.sql_model.product_id)
            .group_by(stmt_time_frame)
        )

        sales_subquery = self._generate_geography_query(query_filter, sales_subquery)
        sales_subquery = query_filter.filter(sales_subquery).subquery()

        date_range_cte = self._generate_date_range_cte(time_frame, query_filter)

        final_stmt = (
            select(date_range_cte.c.time_frame, func.coalesce(sales_subquery.c.units, 0).label("units"))
            .select_from(date_range_cte)
            .outerjoin(sales_subquery, sales_subquery.c.time_frame == date_range_cte.c.time_frame)
            .order_by(date_range_cte.c.time_frame)
        )

        return await paginate(self.session, final_stmt)

    async def get_sales_quantity_per_geography(self, query_filter: SaleFilter) -> Page[GeographyDecimalQuantitySchema]:
        """
        Get the sales quantity across geography locations.

        :param query_filter: Filter object.
        :return: Paginated list of sales quantity across geography locations and geography objects.
        """
        stmt_sum_quantity = label("quantity", func.sum(self.sql_model.quantity))
        stmt_geography_id = label("id", Geography.id)
        stmt_geography_name = label("name", Geography.name)
        stmt_geography_postcode = label("postcode", Geography.postcode)

        stmt = (
            select(
                stmt_sum_quantity,
                func.jsonb_build_object(
                    "id",
                    stmt_geography_id,
                    "name",
                    stmt_geography_name,
                    "postcode",
                    stmt_geography_postcode,
                ).label("geography"),
            )
            .join(Machine, Machine.id == self.sql_model.machine_id)
            .join(Geography, stmt_geography_id == Machine.geography_id)
            .group_by(Geography.id)
            .order_by(Geography.id)
        )

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt, unique=False)

    async def get_conversion_rate(self, query_filter: SaleFilter) -> ConversionRateSchema:
        """
        Get the conversion rate.

        :param query_filter: Filter object.
        :return: Count of new costumers (created_at >= date_from) and
                 count of returning customers (created_at < date_from).
        """
        stmt_customers_new = label(
            "customers_new",
            func.count(func.distinct(MachineUser.user_id)).filter(MachineUser.created_at >= query_filter.date_from),
        )
        stmt_customers_returning = label(
            "customers_returning",
            func.count(func.distinct(MachineUser.user_id)).filter(MachineUser.created_at < query_filter.date_from),
        )

        stmt = (
            select(stmt_customers_new, stmt_customers_returning)
            .join(Machine, Machine.id == MachineUser.machine_id)
            .join(Sale, Sale.machine_id == Machine.id)
        )
        stmt = self._generate_geography_query(query_filter, stmt)

        stmt = query_filter.filter(stmt)
        result = await self.session.execute(stmt)
        row = result.one()

        return ConversionRateSchema(customers_new=row.customers_new, customers_returning=row.customers_returning)

    async def get_sales_by_venue_over_time(self, query_filter: SaleFilter) -> Page[VenueSalesQuantitySchema]:
        """
        Get the sales quantity by venue (source system id) over time.

        :param query_filter: Filter object.
        :return: Paginated list of sales quantity across venue objects.
        """
        stmt_sum_quantity = label("quantity", func.sum(self.sql_model.quantity))
        stmt_source_system = label("venue", self.sql_model.source_system)

        stmt = select(stmt_sum_quantity, stmt_source_system).group_by(stmt_source_system).order_by(stmt_source_system)

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt)

    async def get_sales_quantity_by_category(self, query_filter: SaleFilter) -> Page[CategoryProductQuantityDateSchema]:
        """
        Get the sales quantity by category.

        :param query_filter: Filter object.
        :return: Paginated list of sales quantity across category objects.
        """
        stmt_sum_quantity = label("quantity", func.sum(self.sql_model.quantity))
        stmt_category_id = label("category_id", ProductCategory.id)
        stmt_category_name = label("category_name", ProductCategory.name)
        stmt_product_id = label("product_id", Product.id)
        stmt_product_name = label("product_name", Product.name)
        stmt_sale_date = label("sale_date", func.max(self.sql_model.sale_date))

        stmt = (
            select(
                stmt_sum_quantity,
                stmt_category_id,
                stmt_category_name,
                stmt_product_id,
                stmt_product_name,
                stmt_sale_date,
            )
            .join(Product, Product.id == self.sql_model.product_id)
            .join(ProductCategory, ProductCategory.id == Product.product_category_id)
            .group_by(stmt_category_id, stmt_category_name, stmt_product_id, stmt_product_name)
            .order_by(desc(stmt_sale_date))
        )

        stmt = self._generate_geography_query(query_filter, stmt)
        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt)

    async def export(self, query_filter: ExportSaleFilter) -> list[Sale]:
        """
        Export sales data. This method is used to export sales data in different formats.
        It returns a list of sales objects based on the filter.

        :param query_filter: Filter object.

        :return: List of sales objects.
        """
        stmt = (
            select(
                label("Sale ID", self.sql_model.id),
                label("Venue name", self.sql_model.source_system),
                label("Geography", Geography.name),
                label("Product sold", Product.name),
                label("Product ID", self.sql_model.product_id),
                label("Machine ID", self.sql_model.machine_id),
                label("Machine Name", Machine.name),
                label("Date", self.sql_model.sale_date),
                label("Time", self.sql_model.sale_time),
            )
            .join(Product, Product.id == self.sql_model.product_id)
            .join(Machine, Machine.id == self.sql_model.machine_id)
            .join(Geography, Geography.id == Machine.geography_id)
            .order_by(self.sql_model.sale_date)
        )

        if query_filter.geography_id__in:
            stmt = stmt.where(Geography.id.in_(query_filter.geography_id__in or []))
            setattr(query_filter, "geography_id__in", None)

        stmt = query_filter.filter(stmt)

        return (await self.session.execute(stmt)).mappings().all()  # type: ignore
