from enum import StrEnum


class ExportTypeEnum(StrEnum):
    CSV = "CSV"
    EXCEL = "Excel"


class ExportEntityTypeEnum(StrEnum):
    ACTIVITY_LOG = "activity_log"
    SALE = "sale"
    IMPRESSION = "impression"
