from enum import StrEnum


class DateRangeEnum(StrEnum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

    @property
    def interval(self) -> str:
        """
        :return: The corresponding PostgreSQL interval string.
        """
        return "3 months" if self is DateRangeEnum.QUARTER else f"1 {self.value}"
