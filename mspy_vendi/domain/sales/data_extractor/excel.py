import re
from io import BytesIO

import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from mspy_vendi.domain.data_extractor import BaseDataExtractorClient
from mspy_vendi.domain.machine_impression.schemas import MachineImpressionBulkCreateResponseSchema
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import ExcelSaleCreateSchema, SalesBulkCreateResponseSchema


class ExcelDataExtractor(BaseDataExtractorClient[bytes, MachineImpressionBulkCreateResponseSchema]):
    @staticmethod
    def validate_transaction_id(v: int | float | str) -> int | None:
        """
        Normalize a transaction id from various formats.

        If the value is a string with parentheses (e.g., "1111 (123456789)"),
        it extracts the number inside the parentheses. If the value is NaN (float),
        it returns None.

        :param v: Raw transaction id from Excel.
        :return: Extracted transaction id as int, or None if invalid.
        """
        if isinstance(v, int):
            return v

        if isinstance(v, float):
            return None

        if isinstance(v, str) and not v.isdigit():
            if match := re.search(r"\(([^)]+)\)", v):
                v: str = match.group(1)

        return int(v)

    def _transform_data_frame(self, data_frame: DataFrame):
        """
        Transform and clean the DataFrame for sales import.

        - Uses the first row as column headers.
        - Removes columns not required by ExcelSaleCreateSchema.
        - Normalizes the "Transaction ID" field using `validate_transaction_id`.

        :param data_frame: Raw DataFrame loaded from Excel.
        :return: None.
        """
        data_frame.columns = data_frame.iloc[0]
        data_frame = data_frame.iloc[1:].reset_index(drop=True)

        for column in data_frame.columns:
            if column not in [field.alias for field in ExcelSaleCreateSchema.model_fields.values()]:
                data_frame.drop(columns=[column], inplace=True)

        data_frame.loc[1:, "Transaction ID"] = data_frame.loc[1:, "Transaction ID"].apply(self.validate_transaction_id)

    async def extract(self, data: bytes) -> SalesBulkCreateResponseSchema:
        """
        Extract and validate sales data from an Excel file and persist it to the database.

        - Loads Excel data.
        - Cleans and filters rows with missing required fields.
        - Validates and transforms each row into a Pydantic schema.
        - Calls the SaleManager to persist the records.

        :param data: Excel file as raw bytes.
        :return: Result of the bulk insert operation.
        """
        sale_manager: SaleManager = SaleManager(self.session)
        data_frame: DataFrame = pd.read_excel(BytesIO(data))

        self._transform_data_frame(data_frame)

        required_columns: list = ["Transaction ID", "Product Name", "Machine Name", "Settlement Date and Time (GMT)"]
        filtered_df: DataFrame = data_frame.iloc[1:].dropna(subset=required_columns)

        sale_entities: list[ExcelSaleCreateSchema] = [
            ExcelSaleCreateSchema.model_validate(row.to_dict()) for _, row in filtered_df.iterrows()
        ]

        return await sale_manager.create_batch(sale_entities)
