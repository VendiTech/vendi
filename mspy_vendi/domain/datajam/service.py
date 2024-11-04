from datetime import date

from mspy_vendi.config import log
from mspy_vendi.core.constants import DEFAULT_DATAJAM_DATE
from mspy_vendi.db.engine import get_db_session
from mspy_vendi.domain.datajam.client import DataJamClient
from mspy_vendi.domain.impressions.manager import ImpressionManager


class DataJamService:
    def __init__(self):
        self.datajam_client: DataJamClient = DataJamClient()

    async def process_messages(self) -> None:
        """
        Process a list of messages.

        :param messages: A list of messages to be processed.
        """
        async with get_db_session() as session:
            impression_manager: ImpressionManager = ImpressionManager(session=session)

            list_of_devices = ["JB001690"]  # We will retrieve it from DB after we will fill the data.

            for device_number in list_of_devices:
                latest_date: date = (await impression_manager.get_latest_impression_date()) or DEFAULT_DATAJAM_DATE

                await self.process_by_range(start_date=latest_date, end_date=date.today(), device_number=device_number)

    async def process_by_range(self, start_date: date, end_date: date, device_number: str) -> None:
        """
        Process data from DataJam API by date range.
        """
        log.info("Processing data from DataJam API by date range")
