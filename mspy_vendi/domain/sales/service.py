from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.sales.filter import (
    SaleFilter,
    SaleGetAllFilter,
    StatisticDateRangeFilter,
)
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
)
from mspy_vendi.domain.user.models import User


class SaleService(CRUDService):
    manager_class = SaleManager
    filter_class = SaleGetAllFilter

    async def get_sales_quantity_by_product(self, user: User, query_filter: SaleFilter) -> BaseQuantitySchema:
        return await self.manager.get_sales_quantity_by_product(user, query_filter)

    async def get_sales_quantity_per_range(
        self, user: User, time_frame: DateRangeEnum, query_filter: StatisticDateRangeFilter
    ) -> Page[TimeFrameSalesSchema]:
        return await self.manager.get_sales_quantity_per_range(user, time_frame, query_filter)

    async def get_average_sales_across_machines(self, user: User, query_filter: SaleFilter) -> DecimalQuantitySchema:
        return await self.manager.get_average_sales_across_machines(user, query_filter)

    async def get_average_sales_per_range(
        self, user: User, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[DecimalTimeFrameSalesSchema]:
        return await self.manager.get_average_sales_per_range(user, time_frame, query_filter)

    async def get_sales_quantity_per_category(
        self, user: User, query_filter: SaleFilter
    ) -> Page[CategoryProductQuantitySchema]:
        return await self.manager.get_sales_quantity_per_category(user, query_filter)

    async def get_sales_category_quantity_per_time_frame(
        self, user: User, query_filter: SaleFilter
    ) -> Page[CategoryTimeFrameSalesSchema]:
        return await self.manager.get_sales_category_quantity_per_time_frame(user, query_filter)

    async def get_sales_count_per_time_period(
        self, user: User, query_filter: SaleFilter
    ) -> list[TimePeriodSalesCountSchema]:
        return await self.manager.get_sales_count_per_time_period(user, query_filter)
