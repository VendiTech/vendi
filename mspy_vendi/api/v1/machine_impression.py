from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.domain.machine_impression.schemas import MachineImpressionBulkCreateResponseSchema
from mspy_vendi.domain.machine_impression.service import MachineImpressionService

router = APIRouter(prefix="/machine", default_response_class=ORJSONResponse, tags=[ApiTagEnum.MACHINE_IMPRESSION])


@router.post("/import", response_model=MachineImpressionBulkCreateResponseSchema)
async def import_machine_impression(
    provided_file: UploadFile,
    service: Annotated[MachineImpressionService, Depends()],
    # _: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> MachineImpressionBulkCreateResponseSchema:
    return await service.upload(provided_file)
