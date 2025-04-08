from fastapi import UploadFile

from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.data_extractor.base import BaseDataExtractorClient
from mspy_vendi.domain.machine_impression.factory import MachineImpressionTransformFactory
from mspy_vendi.domain.machine_impression.manager import MachineImpressionManager
from mspy_vendi.domain.machine_impression.schemas import MachineImpressionBulkCreateResponseSchema


class MachineImpressionService(CRUDService):
    manager_class = MachineImpressionManager

    async def upload(self, file: UploadFile) -> MachineImpressionBulkCreateResponseSchema:
        *_, file_type = file.filename.partition(".")
        binary_data: bytes = await file.read()

        data_extractor: BaseDataExtractorClient = MachineImpressionTransformFactory.transform(
            session=self.db_session, file_type=file_type
        )
        return await data_extractor.extract(binary_data)
