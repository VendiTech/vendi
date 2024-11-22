import io

import pandas as pd

from mspy_vendi.domain.data_extractor.base import BaseDataExtractorClient


class ExcelDataExtractor(BaseDataExtractorClient[pd.DataFrame, io.BytesIO]):
    async def extract(self, data: pd.DataFrame) -> io.BytesIO:
        """
        Extract data from the CSV file and provide the Buffer with the actual file.

        :param data: DataFrame with the data.

        :return: Buffer with the actual file.
        """
        response_bytes = io.BytesIO()

        with pd.ExcelWriter(response_bytes, engine="xlsxwriter") as writer:
            data.to_excel(writer, index=False)

        response_bytes.seek(0)

        return response_bytes
