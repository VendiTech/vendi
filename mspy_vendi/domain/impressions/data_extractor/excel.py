from datetime import date, datetime
from io import BytesIO

import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from mspy_vendi.domain.data_extractor import BaseDataExtractorClient
from mspy_vendi.domain.impressions.manager import ImpressionManager
from mspy_vendi.domain.impressions.schemas import ExcelImpressionCreateSchema, ImpressionsBulkCreateResponseSchema


class ExcelDataExtractor(BaseDataExtractorClient[bytes, ImpressionsBulkCreateResponseSchema]):
    @staticmethod
    def normalize_excel_date(excel_date_str: str) -> date | None:
        """
        Normalize the Excel date format (e.g., "01-Jan") to a full date (yyyy-mm-dd) using the current year.
        """
        current_year = date.today().year
        normalized_date = datetime.strptime(f"{excel_date_str}-{current_year}", "%d-%b-%Y")
        return normalized_date.date()

    def _transform_data_frame(self, data_frame: DataFrame) -> None:
        """
        Transform and clean the pandas DataFrane for Impressions import.

        This method performs the following steps:
            - Uses the first row as column headers.
            - Removes columns not required by ExcelImpressionCreateSchema.
            - Normalizes the "Date" field using normalize_excel_date.

        :param data_frame: Raw DataFrane loaded from Excel file.
        :return: None
        """
        for column in data_frame.columns:
            if column not in [field.alias for field in ExcelImpressionCreateSchema.model_fields.values()]:
                data_frame.drop(columns=[column], inplace=True)

        data_frame.loc[0:, "Date"] = data_frame.loc[0:, "Date"].apply(self.normalize_excel_date)

    async def extract(self, data: bytes) -> ImpressionsBulkCreateResponseSchema:
        """
        Extract and validate impressions data from Excel file and persist it to the database.

        - Loads Excel data.
        - Cleans and filters rows with missing required fields.
        - Validates and transforms each row into a Pydantic schema.
        - Calls the ImpressionManager to persist the records.

        :param data: Excel file as raw bytes.
        :return: Result of the bulk insert operation.
        """
        impression_manager: ImpressionManager = ImpressionManager(self.session)
        data_frame: DataFrame = pd.read_excel(BytesIO(data), header=0)

        self._transform_data_frame(data_frame)

        impression_entities: list[ExcelImpressionCreateSchema] = [
            ExcelImpressionCreateSchema.model_validate(row.to_dict()) for _, row in data_frame.iterrows()
        ]

        return await impression_manager.create_batch(impression_entities)
