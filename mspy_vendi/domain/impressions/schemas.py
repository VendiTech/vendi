from datetime import date

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema


class ImpressionBaseSchema(BaseSchema):
    date: date
    total_impressions: int
    temperature: int
    rainfall: int
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: str
    device_number: str


class ImpressionCreateSchema(ImpressionBaseSchema): ...


class ImpressionDetailSchema(ImpressionBaseSchema):
    id: int
