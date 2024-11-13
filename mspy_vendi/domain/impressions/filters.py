import datetime

from pydantic import NonNegativeInt, PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.impressions.models import Impression


class ImpressionFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None
    date_from: datetime.date | None = None
    date_to: datetime.date | None = None

    total_impressions: NonNegativeInt | None = None
    temperature: int | None = None
    rainfall: int | None = None
    source_system: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Impression
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "date"
