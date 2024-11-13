from datetime import datetime, timedelta

from pydantic import PositiveInt, model_validator

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.db import Sale


class StatisticDateRangeFilter(BaseFilter):
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_params(self):
        """
        Check current date range parameters and set default values if they are not set.
        Example:
            - if date_from is not set, it will be set to 30 days ago.
            - if date_to is not set, it will be set to the current date.

        :return: self
        """
        current_datetime = datetime.now()

        if not self.date_from:
            self.set_without_validation("date_from", current_datetime - timedelta(days=30))

        if not self.date_to:
            self.set_without_validation("date_to", current_datetime)

        return self

    class Constants(BaseFilter.Constants):
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


class SaleGetAllFilter(SaleFilter):
    order_by: list[str] | None = ["-id"]
