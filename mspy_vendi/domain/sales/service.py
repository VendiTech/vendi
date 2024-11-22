import io

import pandas as pd
from fastapi.responses import StreamingResponse

from mspy_vendi.core.constants import DEFAULT_EXPORT_TYPES
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.sales.factory import DataExportFactory
from mspy_vendi.domain.sales.filter import (
    ExportSaleFilter,
    SaleFilter,
    SaleGetAllFilter,
    StatisticDateRangeFilter,
)
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    UnitsTimeFrameSchema,
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

    async def get_sales_quantity_per_category(self, query_filter: SaleFilter) -> Page[CategoryProductQuantitySchema]:
        return await self.manager.get_sales_quantity_per_category(query_filter)

    async def get_sales_category_quantity_per_time_frame(
        self, query_filter: SaleFilter
    ) -> Page[CategoryTimeFrameSalesSchema]:
        return await self.manager.get_sales_category_quantity_per_time_frame(query_filter)

    async def get_sales_count_per_time_period(self, query_filter: SaleFilter) -> list[TimePeriodSalesCountSchema]:
        return await self.manager.get_sales_count_per_time_period(query_filter)

    async def get_units_sold(self, query_filter: SaleFilter) -> Page[UnitsTimeFrameSchema]:
        time_frame = DateRangeEnum.MONTH
        return await self.manager.get_units_sold(time_frame, query_filter)

    async def get_sales_quantity_per_geography(self, query_filter: SaleFilter) -> Page[GeographyDecimalQuantitySchema]:
        return await self.manager.get_sales_quantity_per_geography(query_filter)

    async def get_conversion_rate(self, query_filter: SaleFilter) -> ConversionRateSchema:
        return await self.manager.get_conversion_rate(query_filter)

    async def export_sales(self, query_filter: ExportSaleFilter, export_type: ExportTypeEnum) -> StreamingResponse:
        sale_data: list[dict] = await self.manager.export_sales(query_filter)

        file_extension: str = DEFAULT_EXPORT_TYPES[export_type].get("file_extension")
        file_content_type: str = DEFAULT_EXPORT_TYPES[export_type].get("content_type")

        file_name: str = (
            f"Sale Report Start-date: {query_filter.date_from.date()}"
            f" End-date: {query_filter.date_to.date()}.{file_extension}"
        )

        df = pd.DataFrame(sale_data)

        content: io.BytesIO = await DataExportFactory.transform(export_type).extract(df)

        return StreamingResponse(
            content=content,
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition",
                "Content-Disposition": f"""attachment; {file_name=}""",
            },
            media_type=file_content_type,
        )
