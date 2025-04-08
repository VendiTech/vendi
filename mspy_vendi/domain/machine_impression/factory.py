from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.domain.data_extractor.base import BaseDataExtractorClient
from mspy_vendi.domain.machine_impression.data_extractor.excel import ExcelDataExtractor
from mspy_vendi.domain.machine_impression.manager import MachineImpressionManager
from mspy_vendi.domain.machine_impression.schemas import (
    MachineImpressionBulkCreateResponseSchema,
    MachineImpressionCreateSchema,
)


class MachineImpressionTransformFactory:
    @staticmethod
    def transform(session: AsyncSession, file_type: Literal["xlsx"]) -> BaseDataExtractorClient:
        match file_type:
            case "xlsx":
                return ExcelDataExtractor[
                    MachineImpressionCreateSchema,
                    MachineImpressionBulkCreateResponseSchema,
                    MachineImpressionManager,
                ](
                    session=session,
                    create_schema=MachineImpressionCreateSchema,
                    manager_class=MachineImpressionManager,
                )

            case _:
                raise BadRequestError(f"Provided {file_type=} didn't acceptable yet.")
