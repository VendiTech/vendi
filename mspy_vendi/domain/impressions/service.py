from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
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


class ImpressionsService(CRUDService):
    manager_class = ImpressionManager
    filter_class = ImpressionFilter

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
