from fastapi_filter import FilterDepends, with_prefix
from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter, DateRangeFilter
from mspy_vendi.domain.activity_log.enums import EventTypeEnum
from mspy_vendi.domain.activity_log.models import ActivityLog
from mspy_vendi.domain.user.filters import UserFilter


class ActivityLogFilter(DateRangeFilter):
    user_id__in: list[PositiveInt] | None = None
    event_type__in: list[EventTypeEnum] | None = None
    user: UserFilter = FilterDepends(with_prefix("user", UserFilter))

    order_by: list[str] | None = ["-created_at"]

    class Constants(BaseFilter.Constants):
        model = ActivityLog
        date_range_fields = ["date_from", "date_to"]
