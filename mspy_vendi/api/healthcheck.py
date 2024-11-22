from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.broker import redis_source
from mspy_vendi.core.enums import ApiTagEnum, HealthCheckStatusEnum
from mspy_vendi.core.exceptions.base_exception import BadRequestError
from mspy_vendi.domain.healthcheck.schemas import HealthCheckSchema
from mspy_vendi.domain.healthcheck.service import HealthCheckService
from mspy_vendi.domain.sales.tasks import export_task

router = APIRouter(prefix="/health-check", tags=[ApiTagEnum.HEALTH_CHECK], default_response_class=ORJSONResponse)


@router.get("/", response_model=HealthCheckSchema)
async def perform_healthcheck(service: Annotated[HealthCheckService, Depends()]):
    await (
        export_task.kicker()
        .with_labels(identity_key="user_{id}_{entity}")
        .schedule_by_cron(redis_source, "* * * * *", user_id=7)
    )
    db_connection: bool = await service.check_database_connection()

    if db_connection:
        return HealthCheckSchema(status=HealthCheckStatusEnum.SUCCESS)

    raise BadRequestError(HealthCheckStatusEnum.FAILURE)
