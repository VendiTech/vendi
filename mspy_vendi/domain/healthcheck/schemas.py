from mspy_vendi.core.enums import HealthCheckStatusEnum
from mspy_vendi.core.schemas import BaseSchema


class HealthCheckSchema(BaseSchema):
    status: HealthCheckStatusEnum
