from datetime import date, time

from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.sales.models import Sale


class SaleFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None
    date_from: date | None = None
    date_to: date | None = None

    sale_date: date | None = None
    sale_time: time | None = None
    quantity: PositiveInt | None = None
    source_system: str | None = None
    source_system_id: PositiveInt | None = None
    product_id: PositiveInt | None = None
    machine_id: PositiveInt | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Sale
        date_range_fields = ["sale_date"]
