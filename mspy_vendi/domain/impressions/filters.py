from fastapi_filter import FilterDepends, with_prefix
from pydantic import NonNegativeInt, PositiveInt

from mspy_vendi.core.filter import BaseFilter, DateRangeFilter
from mspy_vendi.db import Impression
from mspy_vendi.domain.machine_impression.models import MachineImpression


class StatisticDateRangeFilter(DateRangeFilter):
    class Constants(DateRangeFilter.Constants):
        model = Impression
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "date"


class GeographyFilter(BaseFilter):
    geography_id__in: list[PositiveInt] | None = None

    class Constants(BaseFilter.Constants):
        model = Impression


class ImpressionFilter(DateRangeFilter, GeographyFilter):
    id__in: list[PositiveInt] | None = None

    total_impressions: NonNegativeInt | None = None
    seconds_exposure: int | None = None
    advert_playouts: int | None = None
    source_system: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(DateRangeFilter.Constants):
        model = Impression
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "date"


class MachineImpressionFilter(BaseFilter):
    machine_id__in: list[PositiveInt] | None = None

    class Constants(BaseFilter.Constants):
        model = MachineImpression


class ExportImpressionFilter(StatisticDateRangeFilter, GeographyFilter):
    machine: MachineImpressionFilter | None = FilterDepends(with_prefix("machine", MachineImpressionFilter))
