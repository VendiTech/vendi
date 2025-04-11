from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.domain.data_extractor.base import BaseDataExtractorClient
from mspy_vendi.domain.sales.data_extractor.excel import ExcelDataExtractor


class DataTransformFactory:
    @staticmethod
    def transform(session: AsyncSession, file_type: Literal["xlsx"]) -> BaseDataExtractorClient:
        match file_type:
            case "xlsx":
                return ExcelDataExtractor(session)

            case _:
                raise BadRequestError(f"Provided {file_type=} didn't acceptable yet.")
