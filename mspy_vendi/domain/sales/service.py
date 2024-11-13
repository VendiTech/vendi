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
    DecimalPercentageProductSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    TimeFrameSalesSchema,
)


class SaleService(CRUDService):
    manager_class = SaleManager
    filter_class = SaleGetAllFilter

    async def get_sales_quantity_by_product(self, query_filter: SaleFilter) -> BaseQuantitySchema:
        return await self.manager.get_sales_quantity_by_product(query_filter)

    async def get_sales_quantity_per_range(
        self, time_frame: DateRangeEnum, query_filter: StatisticDateRangeFilter
    ) -> Page[TimeFrameSalesSchema]:
        return await self.manager.get_sales_quantity_per_range(time_frame, query_filter)

    async def get_average_sales_across_machines(self, query_filter: SaleFilter) -> DecimalQuantitySchema:
        return await self.manager.get_average_sales_across_machines(query_filter)

    async def get_average_sales_per_range(
        self, time_frame: DateRangeEnum, query_filter: SaleFilter
    ) -> Page[DecimalTimeFrameSalesSchema]:
        return await self.manager.get_average_sales_per_range(time_frame, query_filter)

    async def get_sales_proportion_per_product(self, query_filter: SaleFilter) -> Page[DecimalPercentageProductSchema]:
        return await self.manager.get_sales_proportion_per_product(query_filter)
