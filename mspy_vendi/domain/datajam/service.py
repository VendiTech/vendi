from datetime import date, timedelta

from domain.impressions.schemas import CreateImpressionSchema

from mspy_vendi.config import log
from mspy_vendi.core.constants import DEFAULT_DATAJAM_DATE
from mspy_vendi.db.engine import get_db_session
from mspy_vendi.domain.datajam.client import DataJamClient
from mspy_vendi.domain.datajam.schemas import DataJamImpressionSchema, DataJamRequestSchema
from mspy_vendi.domain.impressions.manager import ImpressionManager


class DataJamService:
    def __init__(self):
        self.datajam_client: DataJamClient = DataJamClient()

    @staticmethod
    def split_date_ranges(start_date: date, end_date: date) -> list[tuple[str, str]]:
        """
        Split the date range into 30-day segments.

        :param start_date: The start date of the range.
        :param end_date: The end date of the range.

        :return: A list of date ranges.
        """
        date_ranges: list[tuple[str, str]] = []

        while start_date <= end_date:
            # We need to split the date range into 30-day segments
            segment_end = min(start_date + timedelta(days=29), end_date)

            # Add the segment to the list
            date_ranges.append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

            # Define the new start date.
            start_date: date = segment_end + timedelta(days=1)

        return date_ranges

    async def process_messages(self) -> None:
        """
        Process a list of messages.

        :param messages: A list of messages to be processed.
        """
        async with get_db_session() as session:
            impression_manager: ImpressionManager = ImpressionManager(session=session)

            list_of_devices = ["JB001690"]  # We will retrieve it from DB after we will fill the data.

            for device_number in list_of_devices:
                latest_date: date = (
                    await impression_manager.get_latest_impression_date(device_number=device_number)
                ) or DEFAULT_DATAJAM_DATE

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
        log.info("Processing data from DataJam API by date range")

        # Get data from DataJam API
        try:
            data: DataJamImpressionSchema = await self.datajam_client.get_impressions(
                request_data=DataJamRequestSchema(
                    date_from=start_date,
                    date_to=end_date,
                    device_number=device_number,
                )
            )

            # Save data to DB
            async with get_db_session() as session:
                impression_manager: ImpressionManager = ImpressionManager(session=session)

                await impression_manager.create(obj=CreateImpressionSchema(), obj_id=data.device)

        except ...:
            ...
