from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.mixins.export import ExportMixin
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session, get_email_service
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import (
    AdvertPlayoutsBaseSchema,
    AverageExposureSchema,
    AverageImpressionsSchema,
    ExposurePerRangeSchema,
    GeographyImpressionsCountSchema,
    ImpressionsSalesPlayoutsConvertions,
    TimeFrameImpressionsByVenueSchema,
    TimeFrameImpressionsSchema,
)


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
    ) -> Page[TimeFrameImpressionsSchema]:
        return await self.manager.get_impressions_per_range(time_frame, query_filter)

    async def get_impressions_per_geography(
        self,
        query_filter: ImpressionFilter,
    ) -> Page[GeographyImpressionsCountSchema]:
        return await self.manager.get_impressions_per_geography(query_filter)

    async def get_exposure(self, query_filter: ImpressionFilter) -> Page[ExposurePerRangeSchema]:
        return await self.manager.get_exposure(query_filter)

    async def get_average_impressions_count(self, query_filter: ImpressionFilter) -> AverageImpressionsSchema:
        return await self.manager.get_average_impressions_count(query_filter)

    async def get_adverts_playout(self, query_filter: ImpressionFilter) -> AdvertPlayoutsBaseSchema:
        return await self.manager.get_adverts_playout(query_filter)

    async def get_average_exposure(self, query_filter: ImpressionFilter) -> AverageExposureSchema:
        return await self.manager.get_average_exposure(query_filter)

    async def get_impressions_by_venue_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
    ) -> Page[TimeFrameImpressionsByVenueSchema]:
        return await self.manager.get_impressions_by_venue_per_range(time_frame, query_filter)

    async def get_impressions_sales_playouts_convertion_per_range(
        self,
        time_frame: DateRangeEnum,
        query_filter: ImpressionFilter,
    ) -> Page[ImpressionsSalesPlayoutsConvertions]:
        return await self.manager.get_impressions_sales_playouts_convertion_per_range(time_frame, query_filter)
