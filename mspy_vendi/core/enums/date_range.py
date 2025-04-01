from datetime import time
from enum import Enum, StrEnum


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


class ScheduleEnum(StrEnum):
    MINUTELY = "Minutely"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    BI_ANNUALLY = "Bi-Annually"
    ANNUALLY = "Annually"


class TimePeriodBase:
    @property
    def name(self) -> str:
        return self.value[0]

    @property
    def start(self) -> time:
        return self.value[1]

    @property
    def end(self) -> time:
        return self.value[2]


class TimePeriodEnum(TimePeriodBase, Enum):
    MORNING = ("6 AM-6 PM", time(6, 0, 0), time(17, 59, 59))
    EVENING = ("6 PM-8 PM", time(18, 0, 0), time(19, 59, 59))
    NIGHT = ("8 PM-10 PM", time(20, 0, 0), time(21, 59, 59))
    LATE_NIGHT = ("10 PM-12 AM", time(22, 0, 0), time(23, 59, 59))
    MIDNIGHT = ("12 AM-2 AM", time(0, 0, 0), time(1, 59, 59))
    EARLY_MORNING = ("2 AM-6 AM", time(2, 0, 0), time(5, 59, 59))


class DailyTimePeriodEnum(TimePeriodBase, Enum):
    MORNING = ("6 AM-10 AM", time(6, 0, 0), time(9, 59, 59))
    EVENING = ("10 AM-2 PM", time(10, 0, 0), time(13, 59, 59))
    NIGHT = ("2 PM-6 PM", time(14, 0, 0), time(17, 59, 59))
    LATE_NIGHT = ("6 PM-10 PM", time(18, 0, 0), time(21, 59, 59))
    MIDNIGHT = ("10 PM-2 AM", time(22, 0, 0), time(1, 59, 59))
    EARLY_MORNING = ("2 AM-6 AM", time(2, 0, 0), time(5, 59, 59))
