from enum import StrEnum


class ExportTypeEnum(StrEnum):
    CSV = "CSV"
    EXCEL = "Excel"


class ExportEntityTypeEnum(StrEnum):
    SALE = "sale"
    IMPRESSION = "impression"
