import re
from io import BytesIO

import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from mspy_vendi.domain.data_extractor.base import BaseDataExtractorClient
from mspy_vendi.domain.machine_impression.manager import MachineImpressionManager
from mspy_vendi.domain.machine_impression.schemas import (
    MachineImpressionBulkCreateResponseSchema,
    MachineImpressionCreateSchema,
)


class ExcelDataExtractor(BaseDataExtractorClient[bytes, MachineImpressionBulkCreateResponseSchema]):
    @staticmethod
    def validate_machine_number(v: int | float | str) -> int | None:
        """
        Validate input data from the DataFrame.
        If the string coming, we expect that the value will be inside the brackets.

        Example:
        >>> "1111 (123456789)" # Desired value is 123456789
        >>> float("nan") # Will be converted to None

        :param v: Arbitrary value.

        :return: Validated integer or None.
        """
        if isinstance(v, int):
            return v

        if isinstance(v, float):
            return None

        if isinstance(v, str) and not v.isdigit():
            if match := re.search(r"\(([^)]+)\)", v):
                v: str = match.group(1)

        return int(v)

    def _transfrom_data_frame(self, data_frame: DataFrame):
        """
        Perform data transformation on the DataFrame.

        We expect that the DataFrame will have the following columns:
        - Nayax Code
        - DJ NAME
        - Venue Name

        We will drop all columns that are not in the MachineImpressionCreateSchema.model_fields.values().
        We will also validate the Nayax Code column. Apply the validate_machine_number method to the column.

        :param data_frame: DataFrame to transform.

        :return: None
        """
        # Set the first row as the column names.
        data_frame.columns = data_frame.iloc[0]
        # Drop the first row. We don't need it anymore.
        data_frame.drop(0).reset_index(drop=True)

        for column in data_frame.columns:
            if column not in [field.alias for field in MachineImpressionCreateSchema.model_fields.values()]:
                # Drop the column if it's not in the MachineImpressionCreateSchema.model_fields.values()
                data_frame.drop(columns=[column], inplace=True)

        # Validate the Nayax Code column. Apply the validate_machine_number method to the column.
        data_frame.loc[1:, "Nayax Code"] = data_frame.loc[1:, "Nayax Code"].apply(self.validate_machine_number)

    async def extract(self, data: bytes) -> MachineImpressionBulkCreateResponseSchema:
        """
        Extract data from the Excel file and save it to the database.

        :param data: Excel file in bytes.

        :return: MachineImpressionBulkCreateResponseSchema
        """
        machine_impression_manager: MachineImpressionManager = MachineImpressionManager(self.session)
        data_frame: DataFrame = pd.read_excel(BytesIO(data))

        self._transfrom_data_frame(data_frame)

        machine_impression_entities: list[MachineImpressionCreateSchema] = [
            MachineImpressionCreateSchema.model_validate(row.to_dict()) for _, row in data_frame.loc[1:].iterrows()
        ]

        return await machine_impression_manager.create_batch(machine_impression_entities)
