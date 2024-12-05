from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums import ExportEntityTypeEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.mixins.export import ExportMixin
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session, get_email_service
from mspy_vendi.domain.impressions.filters import ExportImpressionFilter, ImpressionFilter
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import (
    AdvertPlayoutsStatisticsSchema,
    AdvertPlayoutsTimeFrameSchema,
    AverageExposureSchema,
    AverageImpressionsSchema,
    ExportImpressionDetailSchema,
    ExposurePerRangeSchema,
    ExposureStatisticSchema,
    GeographyImpressionsCountSchema,
    ImpressionsSalesPlayoutsConvertions,
    TimeFrameImpressionsByVenueSchema,
    TimeFrameImpressionsSchema,
)
from mspy_vendi.domain.user.models import User


class ImpressionService(CRUDService, ExportMixin):
    manager_class = ImpressionManager
    filter_class = ImpressionFilter

    def __init__(
        self,
        db_session: Annotated[AsyncSession, Depends(get_db_session)],
        email_service: Annotated[MailGunService, Depends(get_email_service)] = None,
    ):
        self.email_service = email_service
        super().__init__(db_session)

    async def get_impressions_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[TimeFrameImpressionsSchema]:
        return await self.manager.get_impressions_per_range(time_frame, query_filter, user)

    async def get_impressions_per_geography(
        self,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[GeographyImpressionsCountSchema]:
        return await self.manager.get_impressions_per_geography(query_filter, user)

    async def get_exposure_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[ExposurePerRangeSchema]:
        return await self.manager.get_exposure_per_range(time_frame, query_filter, user)

    async def get_average_impressions_count(
        self, query_filter: ImpressionFilter, user: User
    ) -> AverageImpressionsSchema:
        prev_month_filter = self.manager.generate_previous_month_filter(query_filter)
        prev_month_res: AverageImpressionsSchema = await self.manager.get_average_impressions_count(
            prev_month_filter, user
        )
        res: AverageImpressionsSchema = await self.manager.get_average_impressions_count(query_filter, user)
        return AverageImpressionsSchema(
            previous_month_statistic=prev_month_res.impressions,
            **res.model_dump(exclude={"previous_month_statistic"}),
        )

    async def get_exposure(self, query_filter: ImpressionFilter, user: User) -> ExposureStatisticSchema:
        return await self.manager.get_exposure(query_filter, user)

    async def get_advert_playouts_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[AdvertPlayoutsTimeFrameSchema]:
        return await self.manager.get_advert_playouts_per_range(time_frame, query_filter, user)

    async def get_average_exposure(self, query_filter: ImpressionFilter, user: User) -> AverageExposureSchema:
        return await self.manager.get_average_exposure(query_filter, user)

    async def get_advert_playouts(self, query_filter: ImpressionFilter, user: User) -> AdvertPlayoutsStatisticsSchema:
        prev_month_filter = self.manager.generate_previous_month_filter(query_filter)
        prev_month_res: AdvertPlayoutsStatisticsSchema = await self.manager.get_advert_playouts(prev_month_filter, user)
        res: AdvertPlayoutsStatisticsSchema = await self.manager.get_advert_playouts(query_filter, user)
        return AdvertPlayoutsStatisticsSchema(
            previous_month_statistic=prev_month_res.advert_playouts,
            **res.model_dump(exclude={"previous_month_statistic"}),
        )

    async def get_impressions_by_venue_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[TimeFrameImpressionsByVenueSchema]:
        return await self.manager.get_impressions_by_venue_per_range(time_frame, query_filter, user)

    async def get_impressions_sales_playouts_convertion_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
        user: User,
    ) -> Page[ImpressionsSalesPlayoutsConvertions]:
        return await self.manager.get_impressions_sales_playouts_convertion_per_range(time_frame, query_filter, user)

    async def get_export_data(
        self,
        query_filter: ExportImpressionFilter,
        user: User,
    ) -> Page[ExportImpressionDetailSchema]:
        return await self.export(query_filter, entity=ExportEntityTypeEnum.IMPRESSION, raw_result=False, user=user)
