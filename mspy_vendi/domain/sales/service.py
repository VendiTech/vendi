import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums.date_range import DailyTimePeriodEnum, DateRangeEnum, TimePeriodEnum
from mspy_vendi.core.mixins.export import ExportMixin
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session, get_email_service
from mspy_vendi.domain.sales.filters import (
    SaleFilter,
    SaleGetAllFilter,
    StatisticDateRangeFilter,
)
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import (
    CategoryProductQuantityDateSchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantityStatisticSchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    ProductsCountGeographySchema,
    QuantityStatisticSchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    TimePeriodSalesRevenueSchema,
    UnitsStatisticSchema,
    UnitsTimeFrameSchema,
    VenueSalesQuantitySchema,
)


class SaleService(CRUDService, ExportMixin):
    manager_class = SaleManager
    filter_class = SaleGetAllFilter

    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db_session)],
        email_service: Annotated[MailGunService, Depends(get_email_service)] = None,
    ):
        self.email_service = email_service
        super().__init__(db_session)

    async def get_sales_quantity_by_product(self, query_filter: SaleFilter) -> QuantityStatisticSchema:
        return await self.manager.get_sales_quantity_by_product(query_filter)

    async def get_sales_quantity_per_range(
        self, time_frame: DateRangeEnum, query_filter: StatisticDateRangeFilter
    ) -> Page[TimeFrameSalesSchema]:
        return await self.manager.get_sales_quantity_per_range(time_frame, query_filter)

    async def get_average_sales_across_machines(self, query_filter: SaleFilter) -> DecimalQuantityStatisticSchema:
        return await self.manager.get_average_sales_across_machines(query_filter)

    async def get_average_sales_per_range(
        self, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[DecimalTimeFrameSalesSchema]:
        return await self.manager.get_average_sales_per_range(time_frame, query_filter)

    async def get_sales_quantity_per_category(self, query_filter: SaleFilter) -> Page[CategoryProductQuantitySchema]:
        return await self.manager.get_sales_quantity_per_category(query_filter)

    async def get_sales_category_quantity(self, query_filter: SaleFilter) -> Page[CategoryTimeFrameSalesSchema]:
        return await self.manager.get_sales_category_quantity(query_filter)

    async def get_sales_revenue_per_time_period(self, query_filter: SaleFilter) -> list[TimePeriodSalesRevenueSchema]:
        return await self.manager.get_sales_revenue_per_time_period(TimePeriodEnum, query_filter)

    async def get_units_sold_per_range(
        self, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[UnitsTimeFrameSchema]:
        return await self.manager.get_units_sold_per_range(time_frame, query_filter)

    async def get_units_sold_statistic(self, query_filter: SaleFilter) -> UnitsStatisticSchema:
        return await self.manager.get_units_sold_statistic(query_filter)

    async def get_sales_quantity_per_geography(self, query_filter: SaleFilter) -> Page[GeographyDecimalQuantitySchema]:
        return await self.manager.get_sales_quantity_per_geography(query_filter)

    async def get_conversion_rate(self, query_filter: SaleFilter) -> ConversionRateSchema:
        return await self.manager.get_conversion_rate(query_filter)

    async def get_daily_sales_count_per_time_period(self, query_filter: SaleFilter) -> list[TimePeriodSalesCountSchema]:
        query_filter.date_from = query_filter.date_to = datetime.datetime.now()
        return await self.manager.get_sales_count_per_time_period(DailyTimePeriodEnum, query_filter)

    async def get_sales_by_venue_over_time(self, query_filter: SaleFilter) -> Page[VenueSalesQuantitySchema]:
        return await self.manager.get_sales_by_venue_over_time(query_filter)

    async def get_sales_quantity_by_category(self, query_filter: SaleFilter) -> Page[CategoryProductQuantityDateSchema]:
        return await self.manager.get_sales_quantity_by_category(query_filter)

    async def get_average_products_count_per_geography(
        self, query_filter: SaleFilter
    ) -> Page[ProductsCountGeographySchema]:
        return await self.manager.get_average_products_count_per_geography(query_filter)
