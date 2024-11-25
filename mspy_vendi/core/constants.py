from asyncpg.pgproto.pgproto import timedelta

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
    # ScheduleEnum.MONTHLY: "0 0 1 * *",  # Every month at 00:00
    ScheduleEnum.MONTHLY: "* * * * *",  # TODO: REMOVE, TEMPORARY
    # ScheduleEnum.QUARTERLY: "0 0 1 1,4,7,10 *",  # Every quarter at 00:00
    ScheduleEnum.QUARTERLY: "* * * * *",  # TODO: REMOVE, TEMPORARY
    # ScheduleEnum.BI_ANNUALLY: "0 0 1 1,7 *",  # Every 6 months at 00:00
    ScheduleEnum.BI_ANNUALLY: "* * * * *",  # TODO: REMOVE, TEMPORARY
    # ScheduleEnum.ANNUALLY: "0 0 1 1 *",  # Every year at 00:00
    ScheduleEnum.ANNUALLY: "* * * * *",  # TODO: REMOVE, TEMPORARY
}

# Timedelta values for schedules
DEFAULT_SCHEDULE_TIMEDELTA: dict[ScheduleEnum, timedelta] = {
    ScheduleEnum.MONTHLY: timedelta(days=30),  # Approximate average for a month
    ScheduleEnum.QUARTERLY: timedelta(days=91),  # Approximate (3 months, considering leap years)
    ScheduleEnum.BI_ANNUALLY: timedelta(days=182),  # Approximate (6 months)
    ScheduleEnum.ANNUALLY: timedelta(days=365),  # 1 year (ignoring leap years for simplicity)
}

DEFAULT_EXPORT_TYPES: dict[ExportTypeEnum, dict] = {
    ExportTypeEnum.CSV: {"file_type": "text/csv", "file_extension": "csv"},
    ExportTypeEnum.EXCEL: {
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_extension": "xlsx",
    },
}

CSS_STYLE: str = """
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .email-content {
                background-color: white;
                margin: 0 auto;
                max-width: 600px;
                padding: 20px;
                border: 1px solid #F6B0B1;
                border-radius: 35px;
            }
            .greeting {
                font-size: 20px;
                font-weight: bold;
                color: #2C3344;
            }
            .message {
                font-size: 16px;
                line-height: 1.5;
                margin: 10px 0;
            }

            .container-link {
                display: flex;
                justify-content: center;
            }

            .link {
                display: inline-block;
                margin: 2px auto;
                padding: 17px 25px;
                background-color: #E9EEF9;
                color: #0050C8 !important;
                text-decoration: none;
                border-radius: 20px;
            }

            .link:hover{
                background-color: #fefefe;
            }
            .closing {
                font-size: 16px;
                line-height: 1.5;
            }
            .closing span {
                display: block;
                margin-bottom: 20px;
            }
            .im {
                color: black;
            }
        </style>
    </head>
"""

MESSAGE_FOOTER: str = """
    <p class="message" style="flex-direction: column">
        If you have any questions or need assistance, feel free to contact us anytime at contact@vendi-portal.com.
        We’re here to support you and always available to help!
    </p>
    <p class="closing">
        <span>Thank you, and welcome to Vendi!</span>
        Warm regards,<br>
        Vendi Team
    </p>
"""
