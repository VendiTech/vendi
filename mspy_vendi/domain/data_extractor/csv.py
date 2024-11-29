import io

import pandas as pd

from .base import BaseDataExtractorClient


class CSVDataExtractor(BaseDataExtractorClient[pd.DataFrame, io.BytesIO]):
    async def extract(self, data: pd.DataFrame) -> io.BytesIO:
        """
        Extract data from the Excel file and provide the Buffer with the actual file.

        :param data: DataFrame with the data.

        :return: Buffer with the actual file.
        """
        response_bytes = io.BytesIO()

        data.to_csv(response_bytes, index=False)

        response_bytes.seek(0)

        return response_bytes
