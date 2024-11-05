from datetime import date, datetime, timedelta

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

from mspy_vendi.config import log
from mspy_vendi.core.constants import DEFAULT_DATAJAM_DATE
from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.db.engine import get_db_session
from mspy_vendi.domain.datajam.client import DataJamClient
from mspy_vendi.domain.datajam.schemas import DataJamImpressionSchema, DataJamRequestSchema
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import CreateImpressionSchema

ignore_logger(__name__)


class DataJamService:
    def __init__(self):
        self.datajam_client: DataJamClient = DataJamClient()

    @staticmethod
    def generate_date_year_mapping(start_date: date, end_date: date) -> dict[str, int]:
        """
        Generate a dictionary to map dates to years.
        Dictionary key is the date in "dd-MMM" format, and the value is the year.

        Example:
        >>> {"01-Jan": 2022, "02-Jan": 2022, ...}

        :param start_date: The start date of the range.
        :param end_date: The end date of the range.

        :return: A dictionary with date-year mappings.
        """
        # Create a dictionary to store date-year mappings
        date_year_mapping: dict[str, int] = {}
        current_date: date = start_date

        # Loop through each date in the range and map it to its year
        while current_date <= end_date:
            # Store the date in "dd-MMM" format as the key, and year as the value
            date_str: str = current_date.strftime("%d-%b")
            date_year_mapping[date_str] = current_date.year

            current_date += timedelta(days=1)

        return date_year_mapping

    def get_full_date_in_range(self, start_date: date, end_date: date, input_date: str) -> date:
        """
        Get the full date in the range for the given input date.
        This function helps to detect the year for the input date in the range.

        :param start_date: The start date of the range.
        :param end_date: The end date of the range.
        :param input_date: The input date in "dd-MMM" format. Example: "01-Jan".

        :return: The full date in the range.
        """
        # Look up the year for the input_date in the mapping
        date_year_mapping = self.generate_date_year_mapping(start_date, end_date)

        current_year: int = date_year_mapping.get(input_date, date.today().year)

        # Construct the full date with the found year
        full_date = datetime.strptime(f"{current_year}-{input_date}", "%Y-%d-%b")
        return full_date.date()

    @staticmethod
    def split_date_ranges(start_date: date, end_date: date) -> list[tuple[str, str]]:
        """
        Split the date range into 30-day segments.
        Return the list of date ranges. Each date range is a tuple of start and end dates.

        :param start_date: The start date of the range.
        :param end_date: The end date of the range.

        :return: A list of date ranges.
        """
        date_ranges: list[tuple[str, str]] = []

        while start_date <= end_date:
            # We need to split the date range into 30-day segments
            segment_end: date = min(start_date + timedelta(days=30), end_date)

            # Add the segment to the list
            date_ranges.append((start_date.strftime("%Y-%m-%d"), segment_end.strftime("%Y-%m-%d")))

            # Define the new start date.
            start_date += timedelta(days=30)

        return date_ranges

    async def process_messages(self) -> None:
        """
        Process a list of messages in 30-days segment.

        This function is called by the TaskiqScheduler to process messages.
        For every device, it retrieves the latest date from the database and processes the data from DataJam API.
        And then store the data in the database.
        """
        async with get_db_session() as session:
            impression_manager: ImpressionManager = ImpressionManager(session=session)

            list_of_devices = ["JB001690"]  # We will retrieve it from DB after we will fill the data.

            for device_number in list_of_devices:
                latest_date: date = (
                    await impression_manager.get_latest_impression_date(device_number=device_number)
                ) or date.fromisoformat(DEFAULT_DATAJAM_DATE)

                for start_date, end_date in self.split_date_ranges(latest_date, date.today()):
                    await self.process_by_range(
                        start_date=date.fromisoformat(start_date),
                        end_date=date.fromisoformat(end_date),
                        device_number=device_number,
                    )

    async def process_by_range(self, start_date: date, end_date: date, device_number: str) -> None:
        """
        Process data from DataJam API by date range.
        """
        log.info("Processing data from DataJam API by date range", start_date=start_date, end_date=end_date)

        try:
            # Get data from DataJam API
            data: DataJamImpressionSchema = await self.datajam_client.get_impressions(
                request_data=DataJamRequestSchema(
                    start_date=start_date,
                    end_date=end_date,
                    device_number=device_number,
                )
            )

            # Save data to DB
            async with get_db_session() as session:
                impression_manager: ImpressionManager = ImpressionManager(session=session)

                await impression_manager.create_batch(
                    obj=[
                        CreateImpressionSchema(
                            device_number=impression.device,
                            date=(full_date := self.get_full_date_in_range(start_date, end_date, impression.date)),
                            total_impressions=impression.total_impressions,
                            temperature=impression.temperature,
                            rainfall=impression.rainfall,
                            source_system_id=f"{impression.device}_{full_date}",
                        )
                        for impression in data.device_info
                    ]
                )

        except BadRequestError as err:
            log.info(
                "Error processing data from DataJam API. Continue fetching",
                response=err.content,
                start_date=start_date,
                end_date=end_date,
            )

            sentry_sdk.capture_exception(err)

        except Exception as err:
            log.error("Exception occurred", error=str(err), start_date=start_date, end_date=end_date)

            sentry_sdk.capture_exception(err)

        else:
            log.info("Data processing completed", start_date=start_date, end_date=end_date)
