from fastapi_filter import FilterDepends, with_prefix
from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter, DateRangeFilter
from mspy_vendi.db import Sale
from mspy_vendi.domain.products.models import Product


class StatisticDateRangeFilter(DateRangeFilter):
    class Constants(DateRangeFilter.Constants):
        model = Sale
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "sale_date"


class GeographyFilter(BaseFilter):
    geography_id__in: list[PositiveInt] | None = None

    class Constants(BaseFilter.Constants):
        model = Sale


class ScheduleGeographyFilter(StatisticDateRangeFilter, GeographyFilter):
    pass


class ProductCategoryFilter(BaseFilter):
    product_category_id__in: list[PositiveInt] | None = None

    class Constants(BaseFilter.Constants):
        model = Product


class SaleFilter(StatisticDateRangeFilter, GeographyFilter):
    quantity: PositiveInt | None = None
    source_system_id: PositiveInt | None = None
    product_id__in: list[PositiveInt] | None = None
    machine_id__in: list[PositiveInt] | None = None
    product: ProductCategoryFilter | None = FilterDepends(with_prefix("product", ProductCategoryFilter))

    order_by: list[str] | None = ["-id"]

    class Constants(StatisticDateRangeFilter.Constants):
        model = Sale
        extra_order_by_fields = ["product", "product_category", "amount", "date", "venue"]


class ExportSaleFilter(StatisticDateRangeFilter, GeographyFilter):
    machine_id__in: list[PositiveInt] | None = None
    product_id__in: list[PositiveInt] | None = None
    product: ProductCategoryFilter | None = FilterDepends(with_prefix("product", ProductCategoryFilter))

    order_by: list[str] | None = ["-id"]

    class Constants(StatisticDateRangeFilter.Constants):
        model = Sale
        extra_order_by_fields = ["product", "date", "venue", "geography", "product_id"]


class SaleGetAllFilter(SaleFilter):
    order_by: list[str] | None = ["-id"]
