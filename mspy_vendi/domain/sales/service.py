import datetime
import io
from typing import Annotated

import pandas as pd
from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.config import log
from mspy_vendi.core.constants import CSS_STYLE, DEFAULT_EXPORT_TYPES, MESSAGE_FOOTER
from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum, ScheduleEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session, get_email_service
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
    DailyTimePeriodEnum,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    TimeFrameSalesSchema,
    TimePeriodEnum,
    TimePeriodSalesCountSchema,
    TimePeriodSalesRevenueSchema,
    UnitsTimeFrameSchema,
)
from mspy_vendi.domain.user.schemas import UserScheduleSchema


class SaleService(CRUDService):
    manager_class = SaleManager
    filter_class = SaleGetAllFilter

    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db_session)],
        email_service: Annotated[MailGunService, Depends(get_email_service)],
    ):
        self.email_service = email_service
        super().__init__(db_session)

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

    async def get_sales_revenue_per_time_period(self, query_filter: SaleFilter) -> list[TimePeriodSalesRevenueSchema]:
        return await self.manager.get_sales_revenue_per_time_period(TimePeriodEnum, query_filter)

    async def get_units_sold(self, query_filter: SaleFilter) -> Page[UnitsTimeFrameSchema]:
        time_frame = DateRangeEnum.MONTH
        return await self.manager.get_units_sold(time_frame, query_filter)

    async def get_sales_quantity_per_geography(self, query_filter: SaleFilter) -> Page[GeographyDecimalQuantitySchema]:
        return await self.manager.get_sales_quantity_per_geography(query_filter)

    async def get_conversion_rate(self, query_filter: SaleFilter) -> ConversionRateSchema:
        return await self.manager.get_conversion_rate(query_filter)

    async def send_sales_report(
        self,
        query_filter: ExportSaleFilter,
        content: io.BytesIO,
        file_name: str,
        user: UserScheduleSchema,
        schedule: ScheduleEnum,
    ) -> None:
        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {CSS_STYLE}
            <body>
                <div class="email-content">
                    <p class="message">
                       Your Scheduled report for the provided range:
                       {query_filter.date_from.date()} to {query_filter.date_to.date()} is ready.
                    </p>
                    {MESSAGE_FOOTER}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject=f"{schedule} Sales report for {user.firstname} {user.lastname}",
            html=html_content,
            files=(file_name, content, None),
        )
        log.info(
            "Sent export message was completed.",
        )

    async def export_sales(
        self,
        query_filter: ExportSaleFilter,
        export_type: ExportTypeEnum,
        sync: bool = True,
        user: UserScheduleSchema | None = None,
        schedule: ScheduleEnum | None = None,
    ) -> StreamingResponse | None:
        sale_data: list[dict] = await self.manager.export_sales(query_filter)

        file_extension: str = DEFAULT_EXPORT_TYPES[export_type].get("file_extension")
        file_content_type: str = DEFAULT_EXPORT_TYPES[export_type].get("content_type")

        file_name: str = (
            f"Sale Report Start-date: {query_filter.date_from.date()}"
            f" End-date: {query_filter.date_to.date()}.{file_extension}"
        )

        df = pd.DataFrame(sale_data)

        content: io.BytesIO = await DataExportFactory.transform(export_type).extract(df)

        if sync:
            return StreamingResponse(
                content=content,
                headers={
                    "Access-Control-Expose-Headers": "Content-Disposition",
                    "Content-Disposition": f"""attachment; {file_name=}""",
                },
                media_type=file_content_type,
            )

        return await self.send_sales_report(
            query_filter=query_filter,
            content=content,
            file_name=file_name,
            user=user,
            schedule=schedule,
        )

    async def get_daily_sales_count_per_time_period(self, query_filter: SaleFilter) -> list[TimePeriodSalesCountSchema]:
        query_filter.date_from = query_filter.date_to = datetime.datetime.now()
        return await self.manager.get_sales_count_per_time_period(DailyTimePeriodEnum, query_filter)
