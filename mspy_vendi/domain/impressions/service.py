from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import TimeFrameImpressionsSchema


class ImpressionsService(CRUDService):
    manager_class = ImpressionManager
    filter_class = ImpressionFilter

    async def get_impressions_per_week(self, query_filter: ImpressionFilter) -> Page[TimeFrameImpressionsSchema]:
        time_frame = DateRangeEnum.WEEK
        return await self.manager.get_impressions_per_week(time_frame, query_filter)
