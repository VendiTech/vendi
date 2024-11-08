import datetime

from pydantic import NonNegativeInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.impressions.models import Impression


class ImpressionFilter(BaseFilter):
    id__in: list[NonNegativeInt] | None = None

    date: datetime.date | None = None
    total_impressions: int | None = None
    temperature: int | None = None
    rainfall: int | None = None
    source_system: str | None = None

    # Multi-field search
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Impression
        fields_for_insensitive_search = ["total_impressions", "temperature", "rainfall", "source_system"]
        date_range_fields = ["date"]
