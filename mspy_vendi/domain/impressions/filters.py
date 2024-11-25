import datetime

from pydantic import NonNegativeInt, PositiveInt, model_validator

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.impressions.models import Impression


class ImpressionFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None
    date_from: datetime.datetime | None = None
    date_to: datetime.datetime | None = None

    total_impressions: NonNegativeInt | None = None
    temperature: int | None = None
    rainfall: int | None = None
    source_system: str | None = None

    order_by: list[str] | None = ["-id"]

    @model_validator(mode="after")
    def validate_date_params(self):
        """
        Check current date range parameters and set default values if they are not set.
        Example:
            - if date_from is not set, it will be set to 30 days ago.
            - if date_to is not set, it will be set to the current date.

        :return: self
        """
        current_datetime = datetime.datetime.now()

        if not self.date_from:
            self.set_without_validation("date_from", current_datetime - datetime.timedelta(days=30))

        if not self.date_to:
            self.set_without_validation("date_to", current_datetime)

        return self

    class Constants(BaseFilter.Constants):
        model = Impression
        date_range_fields = ["date_from", "date_to"]
        default_date_range_db_field = "date"
