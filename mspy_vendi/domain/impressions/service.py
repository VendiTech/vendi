from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import (
    GeographyDecimalImpressionTimeFrameSchema,
    GeographyImpressionsCountSchema,
    TimeFrameImpressionsSchema,
)


class ImpressionsService(CRUDService):
    manager_class = ImpressionManager
    filter_class = ImpressionFilter

    async def get_impressions_per_week(self, query_filter: ImpressionFilter) -> Page[TimeFrameImpressionsSchema]:
        time_frame = DateRangeEnum.WEEK
        return await self.manager.get_impressions_per_week(time_frame, query_filter)

    async def get_impressions_per_geography(
        self, query_filter: ImpressionFilter
    ) -> Page[GeographyImpressionsCountSchema]:
        return await self.manager.get_impressions_per_geography(query_filter)

    async def get_average_impressions_per_geography(
        self, time_frame: DateRangeEnum, query_filter: ImpressionFilter
    ) -> Page[GeographyDecimalImpressionTimeFrameSchema]:
        return await self.manager.get_average_impressions_per_geography(time_frame, query_filter)
