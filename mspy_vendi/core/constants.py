from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import ScheduleEnum

MAX_NUMBER_OF_CHARACTERS: int = 100
DEFAULT_SOURCE_SYSTEM: str = "Nayax"

# DataJam API constants
DEFAULT_PROJECT_NAME: str = "Vendi Tech"
DEFAULT_TYPE_DATA: str = "Impression"
DEFAULT_DATAJAM_DATE: str = "2023-11-09"

SERVER_ERROR_MESSAGE: str = "Something went wrong. Try to use this service later"

# Constants for fastapi-filter library
COMPOUND_SEARCH_FIELD_NAME: str = "search"

DEFAULT_DATE_RANGE_FIELDS: list[str] = ["date_from", "date_to"]

DEFAULT_AGE_RANGE_DB_FIELD: str = "birthdate"
DEFAULT_AGE_RANGE_FIELDS: list[str] = ["age_from", "age_to"]

DEFAULT_SCHEDULE_MAPPING: dict[ScheduleEnum, str] = {
    ScheduleEnum.MONTHLY: "0 0 1 * *",  # Every month at 00:00
    ScheduleEnum.QUARTERLY: "0 0 1 1,4,7,10 *",  # Every quarter at 00:00
    ScheduleEnum.BI_ANNUALLY: "0 0 1 1,7 *",  # Every 6 months at 00:00
    ScheduleEnum.ANNUALLY: "0 0 1 1 *",  # Every year at 00:00
}

DEFAULT_EXPORT_TYPES: dict[ExportTypeEnum, dict] = {
    ExportTypeEnum.CSV: {"file_type": "text/csv", "file_extension": "csv"},
    ExportTypeEnum.EXCEL: {
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_extension": "xlsx",
    },
}
