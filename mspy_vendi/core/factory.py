from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.domain.data_extractor import BaseDataExtractorClient, CSVDataExtractor, ExcelDataExtractor


class DataExportFactory:
    @staticmethod
    def transform(file_type: ExportTypeEnum) -> BaseDataExtractorClient:
        match file_type:
            case ExportTypeEnum.CSV:
                return CSVDataExtractor()

            case ExportTypeEnum.EXCEL:
                return ExcelDataExtractor()

            case _:
                raise BadRequestError(f"Provided {file_type=} didn't acceptable yet.")
