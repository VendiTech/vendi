from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.enums import ApiTagEnum, HealthCheckStatusEnum
from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.domain.healthcheck.schemas import HealthCheckSchema
from mspy_vendi.domain.healthcheck.service import HealthCheckService

router = APIRouter(prefix="/health-check", tags=[ApiTagEnum.HEALTH_CHECK], default_response_class=ORJSONResponse)


@router.get("/", response_model=HealthCheckSchema)
async def perform_healthcheck(service: Annotated[HealthCheckService, Depends()]):
    db_connection: bool = await service.check_database_connection()

    if db_connection:
        return HealthCheckSchema(status=HealthCheckStatusEnum.SUCCESS)

    raise BadRequestError(HealthCheckStatusEnum.FAILURE)
