from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter, DateRangeFilter
from mspy_vendi.db import Sale


class StatisticDateRangeFilter(DateRangeFilter):
    class Constants(DateRangeFilter.Constants):
        model = Sale
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "sale_date"


class GeographyFilter(BaseFilter):
    geography_id__in: list[PositiveInt] | None = None

    class Constants(BaseFilter.Constants):
        model = Sale


class SaleFilter(StatisticDateRangeFilter, GeographyFilter):
    quantity: PositiveInt | None = None
    source_system_id: PositiveInt | None = None
    product_id__in: list[PositiveInt] | None = None
    machine_id__in: list[PositiveInt] | None = None


class ExportSaleFilter(StatisticDateRangeFilter, GeographyFilter): ...


class SaleGetAllFilter(SaleFilter):
    order_by: list[str] | None = ["-id"]
